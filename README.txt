LHCBA Voter Roll 2022-23 Dashboard
==================================

What's in this folder
---------------------
index.html    The whole dashboard: layout, styling, charts and the member data
              for all 38 stations (17,859 members) are inside this one file.
photos/       9 image files holding all 13,987 member photos. The page cuts
              each person's photo out of these sheets automatically.
robots.txt    Tells search engines not to index the site.

Keep index.html and the photos folder together, with the same names. If the
photos folder is moved or renamed, members will show their initials instead
of a photo.

Try it on your computer
-----------------------
Unzip the folder and double-click index.html. It opens in your browser and
works fully offline (only the fonts need internet).

Put it live
-----------
Option 1 - Company web server (recommended for this data)
  Ask IT to upload the whole folder to a sub-folder on the cll.edu.pk server,
  e.g. https://<your-server>/lawyers-dashboard/. Any server works (Apache,
  Nginx, IIS, cPanel). Ask them to put it behind a login or the office
  network so only staff can open it.

Option 2 - Cloudflare Pages + Cloudflare Access (free, can restrict access)
  1. Create a free Cloudflare account, go to Workers & Pages > Create >
     Pages > Upload assets, and upload this folder.
  2. In Zero Trust > Access, add an application for the site's address and
     allow only emails ending in @cll.edu.pk. Visitors then sign in with a
     one-time code sent to their email.

Option 3 - Netlify Drop (fastest, but public)
  Go to https://app.netlify.com/drop and drag this folder onto the page. You
  get a live link within a minute. Anyone with the link can open it, and
  password protection needs a paid Netlify plan.

Avoid a public GitHub repository: the names, photos and office addresses
would be downloadable by anyone, not just viewable on the site.

Editing the code
----------------
index.html is plain HTML, CSS and JavaScript, so it opens in any text editor
(Notepad, VS Code).
  - Colours: the --green, --brass, --seal values near the top of <style>.
  - Titles and wording: plain text in the <body> section.
  - Data: the line starting "const D=" near the start of the <script>
    section. It is generated from the voter-list PDFs, so it is easier to
    send new station PDFs to Claude to rebuild than to edit by hand.

About the data
--------------
Source: Lahore High Court Bar Association voter lists 2022-23. Phone numbers
and home addresses were deliberately left out. These lists were issued for
the bar election, so use the dashboard for analysis rather than marketing
or bulk messaging.
