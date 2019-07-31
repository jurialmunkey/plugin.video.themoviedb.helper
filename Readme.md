# TheMovieDB Helper [![License](https://img.shields.io/badge/License-GPLv3-blue)](https://github.com/jurialmunkey/plugin.video.themoviedb.helper/blob/master/LICENSE.txt)


**REQUIRES TMDB API KEY TO WORK**
This Kodi video plugin provides access to TheMovieDb for skinners.
It also provides a handy TheMovieDb navigation tool.
Make sure to add your TheMovieDb API key to the addon's settings.


## TODO:
- Currently in Alpha. Many things to add.
- Person infomation
- Better management of navigation to allow for extendedinfo window replacement


## Possible plugin paths
It is preferable to pass the tmdb_id of the item to the plugin path with `&amp;tmdb_id=`.  
If you don't have tmdb_id, you can instead use `&amp;title=$INFO[ListItem.Title]`  
For better matching when using title, add  `&amp;year=$INFO[ListItem.Year]`


#### Recommended Movie/TV
```
plugin://plugin.video.themoviedb.helper/?info=recommended_movie&amp;tmdb_id=8392
```

```
plugin://plugin.video.themoviedb.helper/?info=recommended_tv&amp;tmdb_id=8392
```


#### Similar Movie/TV
```
plugin://plugin.video.themoviedb.helper/?info=similar_movie&amp;tmdb_id=8392
```

```
plugin://plugin.video.themoviedb.helper/?info=similar_tv&amp;tmdb_id=8392
```

#### Cast for Movie/TV
```
plugin://plugin.video.themoviedb.helper/?info=cast_movie&amp;tmdb_id=8392
```

```
plugin://plugin.video.themoviedb.helper/?info=cast_tv&amp;tmdb_id=8392
```

#### Crew for Movie/TV
```
plugin://plugin.video.themoviedb.helper/?info=crew_movie&amp;tmdb_id=8392
```

```
plugin://plugin.video.themoviedb.helper/?info=crew_tv&amp;tmdb_id=8392
```

#### Reviews Movie/TV
```
plugin://plugin.video.themoviedb.helper/?info=review_movie&amp;tmdb_id=8392
```

```
plugin://plugin.video.themoviedb.helper/?info=review_tv&amp;tmdb_id=8392
```


#### Keywords Movie/TV
```
plugin://plugin.video.themoviedb.helper/?info=keywords_movie&amp;tmdb_id=8392
```

```
plugin://plugin.video.themoviedb.helper/?info=keywords_tv&amp;tmdb_id=8392
```

## Plugin Paths for People
These plugin paths search for info related to a specific person. For instance, you can find all movies starring a particular actor. The tmdb_id is the ID for the person being searched.

#### Movies/TV Starring Cast Member
```
plugin://plugin.video.themoviedb.helper/?info=moviecast_person&amp;tmdb_id=8392
```

```
plugin://plugin.video.themoviedb.helper/?info=tvcast_person&amp;tmdb_id=8392
```

#### Movies/TV With Person as Crew Member
```
plugin://plugin.video.themoviedb.helper/?info=moviecrew_person&amp;tmdb_id=8392
```

```
plugin://plugin.video.themoviedb.helper/?info=tvcrew_person&amp;tmdb_id=8392
```

#### Images of Person
```
plugin://plugin.video.themoviedb.helper/?info=images_person&amp;tmdb_id=8392
```

## Standard Lists (no tmdb_id/title necessary)

#### Popular Movies / TvShows / People
```
plugin://plugin.video.themoviedb.helper/?info=popular_movie
```
```
plugin://plugin.video.themoviedb.helper/?info=popular_tv
```
```
plugin://plugin.video.themoviedb.helper/?info=popular_person
```

#### Top Rated Movies / TvShows
```
plugin://plugin.video.themoviedb.helper/?info=toprated_movie
```
```
plugin://plugin.video.themoviedb.helper/?info=toprated_tv
```

#### Upcoming Movies
```
plugin://plugin.video.themoviedb.helper/?info=upcoming_movie
```

#### TvShows Airing Today
```
plugin://plugin.video.themoviedb.helper/?info=upcoming_tv
```

#### In-Theatres Movies
```
plugin://plugin.video.themoviedb.helper/?info=nowplaying_movie
```


#### TvShows Airing This Week
```
plugin://plugin.video.themoviedb.helper/?info=nowplaying_tv
```

## Search for Movies / TvShows / People
```
plugin://plugin.video.themoviedb.helper/?info=search_movie&amp;query=$INFO[ListItem.Title]&amp;year=$INFO[ListItem.Year]
```
```
plugin://plugin.video.themoviedb.helper/?info=search_tv&amp;query=$INFO[ListItem.TvShowTitle]
```
```
plugin://plugin.video.themoviedb.helper/?info=search_people&amp;query=$INFO[ListItem.Label]
```
