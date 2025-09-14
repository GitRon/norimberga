from abc import abstractmethod

## Dependency injection

> In software engineering, dependency injection (DI) is a programming technique in which an object or function receives
> other objects or functions that it requires, as opposed to creating them internally.

A common use-case is to use DI to encapsulate external APIs. This might be a web-based REST API or a third-party
package.

The general idea is to inject a class which provides all required methods via an interface into a service. This service
is then agnostic about the actual implementation. This leads to a good separation of concerns and in addition, can be
used to write a fake API wrapper to avoid hitting a production API during development or unit-testing.

Django itself uses this pattern a lot, for example, for different types of backends.

    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

Here you can set a specific class to send emails to the console or via SMTP. The rest of the code will never and doesn't
need to know which backend is currently active.

## Example

Let's say you want to connect to the AmazingRecipeAPI service and want to sync recipes with your local system. First,
you would create the interface as an abstract class.

````python
import abc


class RecipeApiService(abc.ABC):

  def _authenticate(self):
    ...

  @abc.abstractmethod
  def get_recipe(self, external_id: int):
    ...
````

Now that you have the interface defined, inherit from it in for your AmazingRecipeAPI use-case.

````python
class AmazingRecipeApiService(RecipeApiService):

  def get_recipe(self, external_id: int):
    ...
````

To avoid hitting this API during development, unit-test etc., create a fake API service which returns static data.

````python
class FakeRecipeApiService(RecipeApiService):

  def get_recipe(self, external_id: int):
    return [Recipe(external_id=external_id)]
````

This pattern also comes in handy if you want to connect to more than one recipe API:


````python
class FastAndUnhealthyRecipeApiService(RecipeApiService):

  def get_recipe(self, external_id: int):
    ...
````
