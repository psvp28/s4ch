# S4CH: Search 4 Computational Hate

This project allows users to map out the temporal evolution of conspiracy theories and disinformation on Twitter. Main paper [here](https://arxiv.org/abs/2302.04450)

## About

We use an embedding-based algorithm to detect relationships between tweets. We construct a “landscape” of tweets. This is essentially a phase space where we map out the evolution of the ideas in the tweetspace. We assume that the hashtags associated with the tweet represent the “idea” conveyed by the tweet. Additionally, the evolutionary landscape is a dynamic space; we aim to infer an evolutionary trajectory between the hashtags from the landscape. We employ an algorithm named “Tagset Analysis”, where we map out the relationship between hashtags based on their co-occurrence in the conversational space.

For every hashtag, we define its “tag-dataset” to be the set of all tweets containing the hashtag in the dataset. Once we extract out a tag-dataset, we find each tweet its “closest relative” tweet. This can be thought of as an embedded vector in an n-dimensional phase space where n is the number of hashtags of interest. We then take tweet pairs with the minimum distance as nodes and join them with a directed edge going from the older tweet to the newer one. Once we do this for every tweet in a tag-dataset, we obtain an evolutionary tree for that hashtag. We repeat the algorithm for all the hashtags of interest. This gives us a set of temporally directed tree graphs that connects tweets containing each hashtag in phase space.

Since tweets can have multiple hashtags and will belong to multiple tagset graphs, we need to infer the relationship between the hashtags by looking at the relationship between each tagset tree. This is achieved by constructing a bipartite graph with the tweets in the first layer interacting with each other by the evolutionary trees and the hashtags in the second, inferred, layer interacting with each other. The edges in the second layer are obtained by looking at the co-occurrence of hashtags in tweets in the first layer; each tweet can be thought of as having a latent edge to the hashtags it contains and the dynamics of the first layer influence the second.

This is achieved by concatenating all the evolutionary trees together and then decomposing each interaction between the tagsets (with multiple hashtags) into interactions between individual hashtags. This essentially “explodes” each interaction into a series of interactions given by all permutations possible between the elements in their respective tagsets. It results in a pairwise comparison of all hashtags.

Running code outputs the edgelist of the hashtags network and nodelist with normalised median time of the hashtag usage. 

![image](https://user-images.githubusercontent.com/74037557/202869761-84325843-04ed-4c05-8d79-f07b755e233c.png)


## How to use

1. Have your tweet data ready in this format as a CSV file at the directory **tweets_file_path**.

| id | id_str | user_screen_name | created_at | hashtags |
|     :---:      |     :---:      |     :---:      |     :---:      |     :---:      |
| tweet id in 'int' format | tweet id in 'str' format | username of the tweeter in 'str' format | timestamp of tweet creation in 'str' format | hashtags in tweet in 'str' of a 'list' |
| 11111111111 | '11111111111' | 'user_name_of_user001' | 'January 1st, 1970 00:00:00 UTC+00:00' | '['twitter', 'tweet', 'example'] |

2. Have a list of hashtags you wish to analyse in a txt file at **hashtags_list_path**.
3. Open 'tagset.py' in a text editor. Fill out the directories in the first few lines.
4. Open 'replacer.py' in a text editor. Fill out the directories in the first few lines, referring to the 'tagset.py' file.
5. Open 'posttag.ipynb'. Enter **input_directory_path** (same as **output_directory_path** in 'replacer.py') and **output_path** (final edgelist and nodelist output directories).
6. Run 'tagset.py' and 'replacer.py' in succession. Then open 'posttag.ipynb' and run the two cells.
7. Open edgelist and nodelist in Gephi (or any other visualisation software) to output your final hashtag network.

## Citing this work

This repo is a part of the work that goes into the paper _"Tracking Fringe and Coordinated Activity on Twitter Leading Up To the US Capitol Attack"_. If you use any part of the methodology, code, or as a starting point, please cite as:

| Vishnuprasad, P.S., Nogara, G., Cardoso, F., Cresci, S., Giordano, S., & Luceri, L. (2023). Tracking Fringe and Coordinated Activity on Twitter Leading Up To the US Capitol Attack. ArXiv, abs/2302.04450. |
|     :---:      |

Vishnu is the corresponding author, please direct your queries to [vishnu.prasad@hdr.qut.edu.au](mailto:vishnu.prasad@hdr.qut.edu.au).
