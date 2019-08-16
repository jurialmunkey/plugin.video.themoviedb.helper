# TheMovieDB Helper [![License](https://img.shields.io/badge/License-GPLv3-blue)](https://github.com/jurialmunkey/plugin.video.themoviedb.helper/blob/master/LICENSE.txt)


## Get Details of an Item
These provide detailed info about an item. Some of the properties require OMDb apikey

#### Find details using TMDb ID
`plugin://plugin.video.themoviedb.helper/?info=details&amp;type=movie&amp;tmdb_id=348`

Types: movie, tv, person  
Accepts: tmdb_id=


#### Find details using IMDb ID
`plugin://plugin.video.themoviedb.helper/?info=find&amp;type=movie&amp;imdb_id=$INFO[ListItem.IMDBNumber]`

Types: movie, tv  
Accepts: imdb_id=


#### Find details using Title
`plugin://plugin.video.themoviedb.helper/?info=details&amp;type=movie&amp;query=$INFO[ListItem.Title]`

Types: movie, tv, person  
Accepts: query=, year=


#### Infolabels and properties returned
ListItem.Labels:  
Title, Plot, Genre, Studio, MPAA, Country, Year, Premiered, Rating, Duration

ListItem.Property(property):  
tmdb_id
Genre.X.Name, Genre.X.ID, Studio.X.Name, Studio.X.ID, Country.X.Name, Country.X.ID
birthday, deathday, aliases, role, born
budget, revenue
awards
metacritic_rating, 
imdb_rating, imdb_votes
rottentomatoes_rating, rottentomatoes_image, rottentomatoes_consensus
rottentomatoes_reviewtotal, rottentomatoes_reviewsfresh, rottentomatoes_reviewsrotten
rottentomatoes_usermeter, rottentomatoes_userreviews


## Discover
Complex searches.  
See https://developers.themoviedb.org/3/discover/movie-discover  
**Examples**  
Movies From Year:  
`plugin://plugin.video.themoviedb.helper?info=discover&amp;type=movie&amp;year=$INFO[ListItem.Year]`

Movies From Studio:  
`plugin://plugin.video.themoviedb.helper?info=discover&amp;type=movie&amp;with_companies=$INFO[ListItem.Studio]`

Movies From Genre:  
`plugin://plugin.video.themoviedb.helper?info=discover&amp;type=movie&amp;with_genres=$INFO[ListItem.Genre]`


**Additional Params for Discover**  
By default discover will lookup the TMDb IDs for the values in with_genres/with_countries etc.
If you already have the TMDb IDs, you can pass those instead and skip the lookup:  
`&amp;with_id=True`

By default discover will provide items matching any values in with_genres/with_countries etc. 
If you only want items that match ALL values, change the with_separator:  
`&amp;with_separator=AND`

Sometimes you will have multiple values separated by '/' but only want the first one. 
e.g. You only want the first studio from ListItem.Studio  
`&amp;with_separator=NONE`

To pass multiple values from different places, separate them with ' / '  
e.g. Getting movies starring first three cast members in info dialog:  
`plugin://plugin.video.themoviedb.helper?info=discover&amp;type=movie&amp;with_cast=$INFO[Container(50).ListItemAbsolute(0).Label]$INFO[Container(50).ListItemAbsolute(1).Label, / ,]$INFO[Container(50).ListItemAbsolute(2).Label, / ,]`



## Other Possible plugin paths
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


