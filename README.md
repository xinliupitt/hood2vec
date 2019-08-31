# hood2vec

This repo contains codes for the visualization app in my work: <a href="https://arxiv.org/abs/1907.11951">hood2vec: Identifying Similar Urban Areas Using Mobility Networks</a>. My work won <a href="https://enterprise.foursquare.com/intersections/article/how-location-technology-can-drive-urban-innovation/">Foursquare Future Cities Data Challenge</a>.

This repo has also been pushed to <a href="https://www.heroku.com/">heroku</a>, which hosts the visualization <a href="https://hood2vec.herokuapp.com/index">app</a>.

- index.py: the main file to process the interactive visualization app
- chi_zipcode_to_dist_midday: A pickle file which saves a dictionary for Chicago in midday period. The key is zip code. Value is a list of zip codes; the list is sorted (ascending) by the distance to the zip code in the key; the distance is measured in hood2vec latent space. The method to generate this file is in <a href="https://arxiv.org/abs/1907.11951">this paper</a>.

The conditions in New York City can also be visualization by applying those pickle files with "nyc" prefix.
