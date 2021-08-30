---
layout: post
title:  "Posting Rmarkdown Outputs on Jekyll Blog"
author: mahmud
categories: [ r, blogging ]
tags: [ tips ]
image: assets/images/thumb/r.png
description: "How to post Rmarkdown Outputs on Jekyll Blog, including estimation from Rstudio and charts and plots"
---

Steps required

- Create a folder inside `assets` and name it `r` or something else.
- Create a .Rmd file and write your entire document inside this, including any calculation and codes for desired charts or plots. 
- Make sure that output format is `md_document` in YAML metadata. Look at a sample below:

	<pre>
	---
	layout: post

	title:  "Sample"

	output: md_document
	---
	</pre>

- Knit the document in Rstudio. 
- Copy the .md file into `_posts` folder. 
- Correct the img path

	Initially the img paths would be something like this: `<img src="2021-01-25-sample_files/figure-markdown_strict/unnamed-chunk-1-1.png" width="100%" />`

	Add `assets/r/` before it, or correct accordingly. 

- Add post metadat. Look at a sample below

	<pre>
	---
	layout: post
	title:  "Title"
	author: mahmud
	categories: [ info, mini ]
	tags: [ stars, series ]
	image: assets/images/
	description: "Sample Description"
---
	</pre>
	
- Publish your new .md file. 