# Web Map

### Movie locations map

This program is created to build a map of film locations.
As a result, there is an HTML-page with a __three-layer map__.

- First layer is the main one with a simple map.
- Second one is with film locations (up to ten) that are the closest to user coordinates.
- Third one is with film locations (up to ten) that are located in user's chosen country.

The module contains *9 functions* which serve for the problem solving.
The program is created for entartainment and searching of movie locations.

All special libraries and downloads are mentioned in requirements.txt.

> To use the program, download main.py and all special requirements and start main.py. 
> You will be asked to enter a movie year, your locations and 
> a country where you would like too see movie locations.

### An example of the program use

```sh
>>> python main.py
Please enter a year you would like to have a map for: 2008
Please enter your location (format: lat, long): 49.83826, 24.02324
Please enter a country you would like to have a map for: Brazil
Map generation is finished. Please have a look at 2008_Brazil_movies_map.html
```

### The map of 2008 films near user (Lviv) and in Brazil.
<img width="960" alt="Brazil_2008_map" src="https://user-images.githubusercontent.com/50978411/107990425-225e6800-6fdd-11eb-9d5d-807c70b865d0.png">


The map as an **HTML file** has a basic HTML structure:
- the first line declares a version of HTML
- the head
- the body

The tags are head, body, links, script, div (to define sections),
style and meta to give an information about the document.

#### Have fun using web map program!