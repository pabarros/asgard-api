from unittest import TestCase
from unittest.mock import Mock

from hollowman.dispatcher import dispatch
from hollowman.hollowman_flask import OperationType


class DispatcherTests(TestCase):
    def test_it_calls_registered_filters_in_order(self):
        filters = [Mock(), Mock()]
        request_app = Mock()
        user = Mock()
        app = Mock()

        dispatch(
            [OperationType.READ], user, request_app, app,
            filters_pipeline={OperationType.READ: filters}
        )

        filters[0].read.assert_called_once_with(user, request_app, app)
        filters[1].read.assert_called_once_with(user, filters[0].read.return_value, app)

    def test_it_doesnt_calls_filters_for_other_operations(self):
        filters = [Mock(), Mock()]
        request_app = Mock()
        user = Mock()
        app = Mock()

        dispatch(
            [OperationType.READ], user, request_app, app,
            filters_pipeline={OperationType.READ: [], OperationType.WRITE: filters}
        )

        for filter in filters:
            filter.assert_not_called()
