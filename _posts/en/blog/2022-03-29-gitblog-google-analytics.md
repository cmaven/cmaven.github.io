---
title: "Tracking Visitors on a GitHub Blog with Google Analytics (GA4)"
description: "Guide to applying Google Analytics GA4 to a GitHub blog to track visitor statistics"
excerpt: "From signing up for Google Analytics GA4 to creating a Measurement ID and wiring it into the Jekyll _config.yml"
date: 2022-03-29
categories: Github_Blog
tags: [GoogleAnalytics, GA4, Jekyll, visitor-stats, traffic-analysis, Minimal-Mistakes]
ref: gitblog-google-analytics
---


:bulb: This post explains how to apply Google Analytics (GA4) to a GitHub blog and track visitor statistics.
{: .notice--info}

# [01]  What is Google Analytics?

> A Web Analytics Service from Google that tracks and reports website traffic.

It lets you monitor visitor statistics for your blog.

# [02]  Setting Up Google Analytics

## Sign Up and Create an Account

- Visit the Google Analytics site to create an account and walk through setup.

  [(link) google analytics](https://analytics.google.com/analytics/web/){:target="_blank"}

  ![01](https://user-images.githubusercontent.com/76153041/160599808-64fb41fd-4fd6-434a-8644-b0c05ccb6f4a.png)

- The account name does not need to match your Google ID.

  ![02](https://user-images.githubusercontent.com/76153041/160599811-2e24ba78-7b77-49e5-99c0-c05729717743.png)

- Use the blog URL as the property name.
- Set the reporting time zone and currency to your locale (e.g., Republic of Korea / KRW).

  ![03](https://user-images.githubusercontent.com/76153041/160599820-648b14d2-62c1-4e85-978d-f2c8a4f69877.png)

- Business information is optional (you can change it later).

  ![04](https://user-images.githubusercontent.com/76153041/160599824-5246bf8a-c903-42e9-9a3d-3752094e19a7.png)

- Accept the Terms of Service.

  ![05](https://user-images.githubusercontent.com/76153041/160599830-496811bb-d455-45c0-9598-8573bb8db175.png)

- Accepting the terms completes the initial setup.
- To actually monitor traffic data, you need to configure a **Data Stream** and create a **Measurement ID**.
- The Measurement ID is added to the GitHub Blog config file so Google Analytics can track the page.
- Google Analytics currently runs as **GA4** (Google Analytics 4) and uses IDs in the `G-XXX` format.
- The previous version, **UA** (Google Analytics 3), used IDs in the `UA-XXX` format.

  > When you search for how to set up Google Analytics, you'll see many posts referencing the UA-XXX tracking ID. Since we created a Google Analytics 4 property above, methods built around UA-XXX won't work correctly.

- A GitHub Blog is a web property, so select **Web** as the platform.
  ![06](https://user-images.githubusercontent.com/76153041/160599835-d09895c9-6a1d-46e2-a922-7f0912d1faf5.png)

- Enter the blog URL as the Website URL; choose any Stream name you like.
  ![07](https://user-images.githubusercontent.com/76153041/160599841-c37fe421-2e8d-4fae-8731-848e3548e59c.png)

- Apply the **Measurement ID** (`G-4DKPW49KWZ` in the screenshot below) to the GitHub Blog.
  ![08](https://user-images.githubusercontent.com/76153041/160599844-e28d5077-03b5-48c9-aa88-171d0d01f5e2.png)

## GitHub Blog Configuration

> Minimal Mistakes theme.

- In `_config.yml`, set `provider` to `google-gtag` and add the `measurement_id` (create the field if it doesn't exist) using the tracking ID above.

  ![18](https://user-images.githubusercontent.com/76153041/160604837-c3e9941b-2a9c-4216-9c90-f1913e8008b8.png)

- Add the following line inside the `<script>` block in `_includes/analytics-providers/google-gtag.html`:
  ```html
  gtag('config', {{ site.analytics.google.measurement_id }});
  ```
  ![10](https://user-images.githubusercontent.com/76153041/160599852-a8f310a6-4c8d-4abc-b8bb-8801a240933e.png)


# [03]  Verifying the Result

- If everything is wired up, refresh the blog and check the Google Analytics home — the stats appear immediately.
-
  ![11](https://user-images.githubusercontent.com/76153041/160600107-010c5616-b57e-429f-98e2-f98998ef35e9.png)
