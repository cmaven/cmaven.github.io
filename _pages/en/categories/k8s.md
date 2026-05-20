---
title: "Kubernetes (English)"
layout: archive
permalink: /en/categories/k8s
author_profile: true
lang: en
sitemap: false
---

{% assign posts = site.categories.K8s | where: "lang", "en" %}
{% for post in posts %}
{% include archive-single-cmaven.html %}
{% endfor %}
