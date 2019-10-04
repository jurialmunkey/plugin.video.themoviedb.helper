# TheMovieDB Helper [![License](https://img.shields.io/badge/License-GPLv3-blue)](https://github.com/jurialmunkey/plugin.video.themoviedb.helper/blob/master/LICENSE.txt)


## Lists based upon another item
TMDbHelper provides several ways to get TMDb lists related to another item.  
All lists require a `&amp;type=` parameter to be specified. Type can be `movie` `tv` or `person`

An additional parameter is required to specify the item that the list will be based upon:  
`&amp;query=$INFO[ListItem.Title]`
`&amp;imdb_id=$INFO[ListItem.IMDBNumber]` 
`&amp;tmdb_id=$INFO[ListItem.Property(tmdb_id)]`  

Skinners can also specify the optional `&amp;year=` parameter to get better results when using `&amp;query=`


#### Recommendations  
`plugin://plugin.video.themoviedb.helper?info=recommendations&amp;type=movie&amp;imdb_id=$INFO[ListItem.IMDBNumber]`

Types: `movie` `tv`  

#### Similar  
`plugin://plugin.video.themoviedb.helper?info=similar&amp;type=movie&amp;imdb_id=$INFO[ListItem.IMDBNumber]`

Types: `movie` `tv`  

#### Cast  
`plugin://plugin.video.themoviedb.helper?info=cast&amp;type=movie&amp;imdb_id=$INFO[ListItem.IMDBNumber]`

Types: `movie` `tv`  

#### Crew  
`plugin://plugin.video.themoviedb.helper?info=crew&amp;type=movie&amp;imdb_id=$INFO[ListItem.IMDBNumber]`

Types: `movie` `tv`  

#### Keywords  
`plugin://plugin.video.themoviedb.helper?info=movie_keywords&amp;type=movie&amp;imdb_id=$INFO[ListItem.IMDBNumber]`

Types: `movie`  

#### Reviews  
`plugin://plugin.video.themoviedb.helper?info=reviews&amp;type=movie&amp;imdb_id=$INFO[ListItem.IMDBNumber]`

Types: `movie` `tv`  

#### Posters  
`plugin://plugin.video.themoviedb.helper?info=posters&amp;type=movie&amp;imdb_id=$INFO[ListItem.IMDBNumber]`

Types: `movie` `tv`  

#### Fanart  
`plugin://plugin.video.themoviedb.helper?info=fanart&amp;type=movie&amp;imdb_id=$INFO[ListItem.IMDBNumber]`

Types: `movie` `tv`  

#### Seasons  
`plugin://plugin.video.themoviedb.helper?info=seasons&amp;type=tv&amp;query=$INFO[ListItem.TvShowTitle]`

Types: `tv`  

#### Episodes in Season  
`plugin://plugin.video.themoviedb.helper?info=episodes&amp;type=tv&amp;query=$INFO[ListItem.TvShowTitle]&amp;season=2`

Types: `tv`  
Requires: `&amp;season=`  

#### Episode Cast  
`plugin://plugin.video.themoviedb.helper?info=episode_cast&amp;type=tv&amp;query=$INFO[ListItem.TvShowTitle]&amp;season=2&amp;episode=1`

Types: `tv`  
Requires: `&amp;season=` `&amp;episode=`  

#### Episode Thumbs  
`plugin://plugin.video.themoviedb.helper?info=episode_thumbs&amp;type=tv&amp;query=$INFO[ListItem.TvShowTitle]&amp;season=2&amp;episode=1`

Types: `tv`  
Requires: `&amp;season=` `&amp;episode=`  

#### Movies an Actor is Cast in  
`plugin://plugin.video.themoviedb.helper?info=stars_in_movies&amp;type=person&amp;query=$INFO[ListItem.Label]`

Types: `person`  

#### TvShows an Actor is Cast in  
`plugin://plugin.video.themoviedb.helper?info=stars_in_tvshows&amp;type=person&amp;query=$INFO[ListItem.Label]`

Types: `person`  

#### Movies a Person is a Crew Member on
`plugin://plugin.video.themoviedb.helper?info=crew_in_movies&amp;type=person&amp;query=$INFO[ListItem.Label]`

Types: `person`  

#### TvShows a Person is a Crew Member on
`plugin://plugin.video.themoviedb.helper?info=crew_in_tvshows&amp;type=person&amp;query=$INFO[ListItem.Label]`

Types: `person`  

#### Images of a Person
`plugin://plugin.video.themoviedb.helper?info=images&amp;type=person&amp;query=$INFO[ListItem.Label]`

Types: `person`  

#### All Movies in a Collection (aka Set)  
`plugin://plugin.video.themoviedb.helper?info=collection&amp;type=movie&amp;query=$INFO[ListItem.Set]`

Types: `movie`  
