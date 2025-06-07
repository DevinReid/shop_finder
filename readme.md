# Shop Finder


make a copy of the search logs folder either before or after each new project for orgnaization
2. update list of excluded retailers in excluded_retailers.csv
to search, fill out search config. in this format
Skip?,Status,city,lat,lng,radius,query
No,,Charlotte,35.2271,-80.56738338817802,25000,witch store

mark skip as no 
leave status blank
add city name
add latitude and longitude, these can be found on line or genreated with an LLM
Pick a kilometer radius to search, At a max of 50000 KM
Finally add your search term

The code is designed to split if it thinks it needs to so start with the center of each city, and then run it again after new smaller radius circles have been added.  Warning this gests exponetially more expensive if the search yeilds results after many splits

Google places can only give 60 results at a time, if a search hits 60 for an area, it is assumed thwere are more and splits into 5-7 smaller cicles. 
This costs 1-3 api calls per search just to get the List, and 1 for each unique website found and scraped, so a posibility of 63 api calls per search area.
Again it is recomended to fill out the excluded retailers to avoid paying for large companies and box stores less likely to offer wholesale from small vendors

make sure config.py is set up to account for all of your copied files for this search


delete search_map.html for new projects, iot will be regenerated with your code.

run this to make this work doesnt work with play buton invscode anymore
python -m shop_finder.shopFinder