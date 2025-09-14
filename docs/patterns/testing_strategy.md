## Testing strategy

We only use PyTest for creating backend unittests.

## Unit tests

Here are a few rules to keep in mind when writing unittests:

* The structure of the `tests/` package reflects the structure of the production code
* One test file contains only one test class if you use class-based tests. If this contradicts the rule about the
  structure, create a new package for the given file with the files' name and sort in the tests there.
* Unittests are atomic, meaning they will cover only one test case. Avoid large tests covering every case.
* Write at least one test per function or method.
* Have one unittest per code branch in your testee but don't overengineer. Have one test case per edge-case, not more.
* Stick to the AAA pattern when writing tests: Arrange / Act / Assert
* The name of a test method will reflect the testee and the test case. Stick to this pattern:
  `test_[TESTEE]_[TEST_CASE]`. Don't add the class name to the test functions name. It is already set in the test class
  name.
* Try to keep the test class setup as limited as possible to avoid overhead
* When testing exceptions, ensure that you assert the error message and not just the exception class
* Avoid loops and strong abstractions since they make the test harder to understand and change.
* Keep unittests simple and understandable.
* Use `assertRaisesMessage` instead of `assertRaises` to avoid false positives
* Use `assertIs()` instead of `assertTrue` or `assertFalse`  to have more precise tests
* Use mocking as seldom as possible for first-party code since it tests the implementation rather than the
  functionality. Mostly, a happy-path test is better than mocking.
* If you mock, always use `import mock` for mockings to have a consistent way of working with `patch` 
  (`mock.patch` instead of `patch`)
* Ensure that you don't forget to create a `__init__.py` file per new Python package you've created. Otherwise,
  unittests won't be executed.
* Never create objects directly. Always use a factory_boy factory.
* Try to create objects from factories in batches to optimize runtime
* Use semantically useful names like "manufacturer_with_product_id" instead of "mf1"
* Avoid type-hints in variable names like `mymodel_qs`.
* Ensure that all code branches are covered. This doesn't say anything about test quality but at least gives the
  maintainers some peace of mind when updating packages.
