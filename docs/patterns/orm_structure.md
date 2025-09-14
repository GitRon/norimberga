# ORM structure

This part covers the way we want to structure our ORM / query-related code.

## Custom QuerySets (CQS)

* Inherited / overwritten QuerySet class of a given model
* Are named `class MyModelQuerySet()`
* Contains atomic queryset methods (only one operation per method)
  * Take care that complex queries with `Q` or other database operations are still atomic if they do one thing
* Always return a QuerySet of the same model
* Examples
  * `filter(is_active=True)`
  * `exclude(Q(is_active=False) | Q(end_date__isnull=False))`

## Managers

* Registered via the model
* Are named `class MyModelManager()`
* Contain everything that's query-related to the same model but never queries to other models
  * Take care: It's allowed to follow foreign-key relations via the double-dunder notation `field__other`
* Examples
  * `aggreate_hours_spent()`
  * `create_record()`

## Selectors

* Chain CQS and manger methods to fetch data for a specific use-case
* Are functions and live in `my_app/selectors/my_model.py`
* Are called like the use case they support (`get_all_active_users_in_timespan`)
* Prefer to take simple arguments if possible (`user_id` instead of `User` object)

## Models

We try to avoid the fat-model approach to avoid overloading the database layer with just too many things.

In the past, our models tended to grow huge and include a lot of functionality, which was not just related to the
model. To restrict the growth of our models, we want to set a couple of rules in place to reduce this tendency.

Model methods can...
* ...be utility functions related to the model instance
* ...perform calculations or queries (using CQS) on existing data
* ...extend or overwrite methods of the parent class (e.g. clean, save, ...)

Model methods should not...
* ...require an import from another model
* ...be static or provide anything unrelated to the instance
* ...manipulate existing data
* ...meet the requirements to be implemented as a selector or manager
* ...execute a query

## General rules

* Low-level database operations (usually from `django.db`) are not supposed to live outside CQS, manager or selectors
* CQS and mangers are in one file per model in `my_app/managers/my_model.py`, selectors live in another file per model
  in `my_app/selectors/my_model.py`
* CQS are registered via the manager like this: `class MyModelManager(models.Manager.from_queryset(MyModelQuerySet))`
