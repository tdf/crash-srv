# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from .processor import MinidumpProcessor

from uwsgidecoratorsfallback import spool

from subprocess import CalledProcessError

from django.core.exceptions import ObjectDoesNotExist

from django.db import IntegrityError

import logging

logger = logging.getLogger(__name__)

@spool
def do_process_uploaded_crash(env):
    minproc = MinidumpProcessor()
    try:
        minproc.process(env['crash_id'])
    except CalledProcessError as e:
        logger.warn('error processing: %s with error %s - moving task to breaking spools'%(env['crash_id'], str(e)))
        do_process_uploaded_crash.spool({'crash_id':env['crash_id'], 'spooler': '/srv/crashreport/crash/breaking_spools'})
        return -2
    except IntegrityError as e:
        logger.critical('error processing: %s with integrityerror %s - moving task to breaking spools'%(env['crash_id'], str(e)))
        do_process_uploaded_crash.spool({'crash_id':env['crash_id'], 'spooler': '/srv/crashreport/crash/breaking_spools'})
        return -2
    except ObjectDoesNotExist as e:
        logger.critical('error processing: %s with DoesNotExist error %s - moving task to breaking spools'%(env['crash_id'], str(e)))
        do_process_uploaded_crash.spool({'crash_id':env['crash_id'], 'spooler': '/srv/crashreport/crash/breaking_spools'})
        return -2
    except ValueError as e:
        logger.critical('error processing: %s with ValueError %s - moving task to breaking spools'%(env['crash_id'], str(e)))
        do_process_uploaded_crash.spool({'crash_id':env['crash_id'], 'spooler': '/srv/crashreport/crash/breaking_spools'})
        return -2

    logger.info('processed: %s' % (env['crash_id']))
    return -2

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
