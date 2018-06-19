# PodRacer

A simple Flask web application for managing podcast content, using gpodder.net's API. You need a [gpodder.net account](https://gpodder.net/) in order to sign in to PodRacer.

[![Home page display](/screenshots/display_ex1.png "Visual of the home page.")](http://podracer.herokuapp.com)


### Site Features

- **Summary of Subscriptions:** The main page summarizes the podcasts (across all devices) that the user currently subscribed to, including key information such as: title, description, subscriber count and a link to the podcast's website.

- **Search Functionality:** The user can do a quick search for podcasts by a simple search query, or choose more advanced searching methods such as by top genres and by popularity (subscriber count).

- **Recent Episodes + Smart Sorting:** A list of the episodes released in the previous week (up to 7 days before current time) is available on the home page, with embedded playable links. This list is sorted by podcast frequency, such that podcasts with more episodes released in the past week are bubbled to the top, so that users can catch up on them first. However, the sorting algorithm also distributes the frequent episodes equally such that users are not inundated with multiple episodes from the same podcast at one time.

#### Bonus Features

- **Suggestions from gpodder:** Users can see gpodder's top 5 recommendations for podcasts to subscribe to, based on the user's current subscriptions.

- **Suggestions using machine learning:** Unsupervised learning to determine which podcasts are most similar to a user's subscriptions. A simple (disclaimer: simple!) K-means clustering algorithm is applied to the user's subscribed podcasts as well as the 100 most popular podcasts, and 5 popular podcasts that are clustered together with the user's subscriptions are recommended to the user. The features used are the tokenized and transformed vectors of podcast descriptions.

### Miscellaneous

- All code written is my own, except for CSS/HTML/JavaScript styling templates taken from [Landing Page](https://github.com/BlackrockDigital/startbootstrap-landing-page).

- This is submitted for Capital One's Software Engineering Summit Challenge 2018.

- [The original hero](https://www.youtube.com/watch?v=Hn2OEZ0HFjE).
