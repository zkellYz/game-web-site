from typing import Union

from django.db.models import Count, Prefetch
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView
from django.views.generic.base import View
from django.views.generic.edit import DeleteView
from django.utils.decorators import method_decorator

from core.mixins import OrderingMixin, MustSingleRequiredMixin, MustMultipleRequiredMixin
from game.models import Game, Musts, Genre, Platform
from game.utils import GameTweetsParser


class AbstractGameView:
    model = Game


class AbstractMustsView:
    model = Musts


class GameListView(MustMultipleRequiredMixin, OrderingMixin, AbstractGameView, ListView):
    template_name = 'game/games.html'
    available_orderings = ['name', 'date_release', 'rating__critics']
    available_filtering = ['name', 'genres', 'platforms']
    paginate_by = 20

    @staticmethod
    def apply_filter(queryset, key: str, value: Union[str, list]):
        key = f"{key}{'__icontains' if isinstance(value, str) else '__name__in'}"
        return queryset.filter(**{key: value})

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = (
            queryset
            .filter(is_active=True)
            .prefetch_related(
                Prefetch(
                    lookup='genres',
                    queryset=Genre.objects.all(),
                    to_attr='prefetched_genres'
                )
            )
            .order_by('cover')
        )

        for key in self.available_filtering:
            value = self.request.GET.get(key)
            if value:
                if ',' in value:
                    value = value.split(',')
                queryset = self.apply_filter(queryset, key, value)

        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['genres'] = Genre.objects.values_list('name', flat=True)
        context['platforms'] = Platform.objects.values_list('name', flat=True)
        return context


class GameView(LoginRequiredMixin, PermissionRequiredMixin, MustSingleRequiredMixin, AbstractGameView, DetailView):
    template_name = 'game/game.html'
    permission_required = 'game.view_game'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['tweets'] = GameTweetsParser().parse(self.object.name)
        return context


@method_decorator(csrf_exempt, name='dispatch')
class MustView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['game.add_musts', 'game.delete_musts']

    def post(self, request, *args, **kwargs):
        game_obj = Game.objects.filter(id=self.kwargs['pk'])
        must_obj = Musts.objects.filter(game=game_obj.first(), user=request.user)
        if must_obj.exists():
            must_obj.first().delete()
        else:
            Musts(game=game_obj.first(), user=request.user).save()
        return HttpResponse(status=200)


class GameDeleteView(PermissionRequiredMixin, AbstractGameView, DeleteView):
    success_url = '/'
    permission_required = ['game.view_musts', 'game.delete_game']


class MustsListView(LoginRequiredMixin, AbstractMustsView, ListView):
    template_name = 'game/musts.html'

    def get_queryset(self):
        return (
            super().get_queryset()
            .filter(user=self.request.user)
            .annotate(users_added=Count('game__name'))
        )
