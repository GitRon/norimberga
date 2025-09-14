# Mono-app approach

A Django app should be a self-contained package that - at least in theory - can be moved via plug-and-play to another
Django project. In some regards, think of Django apps as third-party packages, which are in the Django world app, too.

Therefore, it's important not to hard-wire apps together. Most projects use apps as some kind of domain but there are no
clear boundaries where one app ends and another one starts.

To ensure longevity and maintainability of your application, follow Django's own recommendations and use a "mono-app"
approach. This means that most of your business logic lives inside a single Django app.

This app can be structured with Python packages in any way you seem fit. If you find code that's 100% project agnostic
and could live inside a third-party package, you've found a candidate for another real Django app.

If you've created another app, note that your main app (usually named like your application) can know (and import) the
other app, BUT NOT THE OTHER WAY AROUND. Your "satellite" apps cannot know about your business logic. If they do, you're
starting to create a big ball of mud.

Since it's quite easy to start this antipattern and miss it in code reviews, having some kind of tooling in place is a
good idea. As Kraken pointed out, your architecture is as good as your tooling.

Therefore, we've created a helper in the Ambient toolbox, which will
create [import-linter](https://pypi.org/project/import-linter/) contracts for your
project: https://ambient-toolbox.readthedocs.io/en/latest/features/import_linter.html
