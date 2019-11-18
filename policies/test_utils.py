import os

try:
    from pybfe.datamodel.policy import (
        STATUS_FAIL, STATUS_PASS
    )
    TEST_STATUS_FAIL = STATUS_FAIL
    TEST_STATUS_PASS = STATUS_PASS
except:
    TEST_STATUS_PASS = u"Pass"
    TEST_STATUS_FAIL = u"Fail"


def record_results(bf, status, message):

    session_type = os.environ.get('SESSION_TYPE')

    if session_type == 'bfe':
        if status == TEST_STATUS_PASS:
            bf.asserts._record_result(True, status=STATUS_PASS,
                                      message=message)
        elif status == TEST_STATUS_FAIL:
            bf.asserts._record_result(False, status=STATUS_FAIL,
                                      message=message)
        else:
            raise Exception

