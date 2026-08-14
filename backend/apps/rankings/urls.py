from django.urls import path

from apps.rankings.views import RankingListView

urlpatterns = [
    path("", RankingListView.as_view(), name="ranking-list"),
]