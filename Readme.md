# TheMovieDB Helper [![License](https://img.shields.io/badge/License-GPLv3-blue)](https://github.com/jurialmunkey/plugin.video.themoviedb.helper/blob/master/LICENSE.txt)


**REQUIRES TMDB API KEY TO WORK**
This Kodi video plugin provides access to TheMovieDb for skinners.
It also provides a handy TheMovieDb navigation tool.
Make sure to add your TheMovieDb API key to the addon's settings.


## TODO:
- Currently in Alpha. Many things to add.
- Complex searches


## Possible plugin paths
Provide the TMDb ID to the plugin for best results  
Can search by IMDb ID or Title + Year if you don't have TMDb  
Most paths require you to specify the type: movie, tv, person
Type: `&amp;type=movie`  
TMDb ID: `&amp;tmdb_id=348`  
IMDb ID: `&amp;imdb_id=$INFO[ListItem.IMDBNumber]`  
Search: `&amp;query=$INFO[ListItem.Title]&amp;year=$INFO[ListItem.Year]`  


#### Cast
`plugin://plugin.video.themoviedb.helper/?info=cast&amp;type=movie`

Types: movie, tv  
Accepts: tmdb_id=, imdb_id=, query=, year=


#### Crew
`plugin://plugin.video.themoviedb.helper/?info=crew&amp;type=movie`

Types: movie, tv  
Accepts: tmdb_id=, imdb_id=, query=, year=


#### Recommendations
`plugin://plugin.video.themoviedb.helper/?info=recommendations&amp;type=movie`

Types: movie, tv  
Accepts: tmdb_id=, imdb_id=, query=, year=


#### Similar
`plugin://plugin.video.themoviedb.helper/?info=similar&amp;type=movie`

Types: movie, tv  
Accepts: tmdb_id=, imdb_id=, query=, year=


#### Keywords for Movie
`plugin://plugin.video.themoviedb.helper/?info=movie_keywords&amp;type=movie`

Types: movie  
Accepts: tmdb_id=, imdb_id=, query=, year=


#### Movies with Keyword
`plugin://plugin.video.themoviedb.helper/?info=keyword_movies&amp;type=movie`

Types: movie  
Accepts: tmdb_id=


#### Movies the Cast Member Stars In
`plugin://plugin.video.themoviedb.helper/?info=stars_in_movies&amp;type=movie`

Types: movie  
Accepts: tmdb_id=


#### Tv Shows the Cast Member Stars In
`plugin://plugin.video.themoviedb.helper/?info=stars_in_tvshows&amp;type=tv`

Types: tv  
Accepts: tmdb_id=


#### Movies the Person was Crew Member on
`plugin://plugin.video.themoviedb.helper/?info=crew_in_movies&amp;type=movie`

Types: movie  
Accepts: tmdb_id=


#### Tv Shows the Person was Crew Member on
`plugin://plugin.video.themoviedb.helper/?info=crew_in_tvshows&amp;type=tv`

Types: tv  
Accepts: tmdb_id=


#### Images of the Person
`plugin://plugin.video.themoviedb.helper/?info=images&amp;type=image`

Types: image  
Accepts: tmdb_id=


#### Search for Items Matching Query
`plugin://plugin.video.themoviedb.helper/?info=search&amp;type=movie`

Types: movie, tv, person  
Accepts: query=, year=


#### Find details using IMDb ID
`plugin://plugin.video.themoviedb.helper/?info=find&amp;type=movie`

Types: movie, tv  
Accepts: imdb_id=


#### Popular Movies / TV / People
`plugin://plugin.video.themoviedb.helper/?info=popular&amp;type=movie`

Types: movie, tv, person  


#### Top Rated Movies / TV
`plugin://plugin.video.themoviedb.helper/?info=top_rated&amp;type=movie`

Types: movie, tv  


#### Upcoming Movies
`plugin://plugin.video.themoviedb.helper/?info=upcoming&amp;type=movie`

Types: movie  


#### Airing Today TV
`plugin://plugin.video.themoviedb.helper/?info=airing_today&amp;type=tv`

Types: tv  


#### In Theatres Movies
`plugin://plugin.video.themoviedb.helper/?info=now_playing&amp;type=movie`

Types: movie  


#### Currently Airing Tv Shows
`plugin://plugin.video.themoviedb.helper/?info=on_the_air&amp;type=tv`

Types: tv  


