# Services

A service is (mostly) a Python class that provides a home for a certain business logic. It's not an abstraction layer in
any form.

Services have a defined entry point (mostly a `process()` method) and contain 0-n protected methods (starting with an
underscore) and their name ends with service, like "HelloWorldService".

They encapsulate business logic which is unique to the application in a testable and understandable manner.

They should not query or write data to the database directly, but call selectors or managers for that.

Ensure that input parameters are understandable and don't bloat the context you need to understand to work with this
service. If possible, pass IDs instead of objects and use kwarg-only dataclasses instead of (complex) dictionaries.

Avoid multipurpose services. This is an antipattern which will render most of a services benefits useless.

A service might be also called a "use-case". It might help to think about a service as a specific use case, like
"ShippingCalculationService".

Note that you might not need a class. If you don't need to split up your logic for testing or structuring purposes, take
the simple road and use a function.

Services live inside a Python file having a similar name like the service: "HelloWorldService" lives in
`myapp/services/hello_world.py`.
