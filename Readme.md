# TheMovieDB Helper [![License](https://img.shields.io/badge/License-GPLv3-blue)](https://github.com/jurialmunkey/plugin.video.themoviedb.helper/blob/master/LICENSE.txt)


## Lists based upon another item
TMDbHelper provides several ways to get TMDb lists related to another item.  
All lists require a `&amp;type=` paramater to be specified. Type can be `movie` `tv` or `person`

#### Recommendations
`plugin://plugin.video.themoviedb.helper?info=recommendations&amp;type=movie&amp;imdb_id=$INFO[ListItem.IMDBNumber]`

Required paramaters:
`&amp;type=movie|tv|person`

Optional paramaters:
