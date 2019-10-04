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


## Default Lists  
These lists are bsed upon trends such as recent releases or popularity. Only a type paramater is required.

#### Popular  
`plugin://plugin.video.themoviedb.helper?info=popular&amp;type=movie`

Types: `movie` `tv` `person`  

#### Top Rated  
`plugin://plugin.video.themoviedb.helper?info=top_rated&amp;type=movie`

Types: `movie` `tv`   

#### Upcoming  
`plugin://plugin.video.themoviedb.helper?info=upcoming&amp;type=movie`

Types: `movie`  

#### Airing Today  
`plugin://plugin.video.themoviedb.helper?info=airing_today&amp;type=tv`

Types: `tv`  

#### Now Playing In Theatres  
`plugin://plugin.video.themoviedb.helper?info=now_playing&amp;type=movie`

Types: `movie`  

#### Currently Airing (in the last week)  
`plugin://plugin.video.themoviedb.helper?info=on_the_air&amp;type=tv`

Types: `tv`   


## Search  
Provides a list of items with titles matching the search query.  
`plugin://plugin.video.themoviedb.helper?info=search&amp;type=movie&amp;query=$INFO[ListItem.Label]`  

Types: `movie` `tv` `person`

## Discover  
More complex searching for items of a specific type that much several parameters:  
`plugin://plugin.video.themoviedb.helper?info=discover&amp;type=movie&amp;with_cast=$INFO[ListItem.Label]`  

Types: `movie` `tv` 

Optional Parameters:  
`&amp;with_cast=`  Includes items that have one of the specified people as a cast member  
`&amp;with_crew=`  Includes items that have one of the specified people as a crew member  
`&amp;with_people=`  Includes items that have one of the specified people as a cast or crew member
`&amp;with_companies=`  Includes items from a matching movie studio  
`&amp;with_genres=`  Includes items with a matching genre  
`&amp;without_genres=`  Excludes items with a matching genre  
`&amp;with_id=True`  Use this parameter if passing a tmdb_id to the above instead of a query

## Optional Parameters for ALL Lists  
Only include items that have the specified key that matches the specified value.  
`&amp;filter_key=KEY&amp;filter_value=VALUE`  

Exclude all items that have the specified key that matches the specified value.  
`&amp;exclude_key=KEY&amp;exclude_value=VALUE`  

Example:
`plugin://plugin.video.themoviedb.helper/?info=crew_in_movies&amp;type=person&amp;filter_key=job&amp;filter_value=Director&amp;query=$INFO[ListItem.Director]&amp;exclude_key=title&amp;exclude_value=$INFO[ListItem.Title]`  
This plugin path will get all movies were the Director was a crew member and their job was director. The currently selected movie will be excluded from the list.


## Detailed Item  
`plugin://plugin.video.themoviedb.helper/?info=details&amp;type=movie&amp;query=$INFO[ListItem.Title]`  

Provides additional details about the current item. 
