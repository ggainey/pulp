# -*- coding: utf-8 -*-
#
# Copyright © 2014 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

import unittest

from mock import patch

from pulp.server.async.tasks import TaskResult
from pulp.server.tasks import consumer


class TestBind(unittest.TestCase):

    @patch('pulp.server.tasks.consumer.managers')
    def test_bind_no_agent_notification(self, mock_bind_manager):
        binding_config = {'binding': 'foo'}
        agent_options = {'bar': 'baz'}
        result = consumer.bind('foo_consumer_id', 'foo_repo_id', 'foo_distributor_id',
                               False, binding_config, agent_options)

        mock_bind_manager.consumer_bind_manager.return_value.bind.assert_called_once_with(
            'foo_consumer_id', 'foo_repo_id', 'foo_distributor_id',
            False, binding_config)

        self.assertEquals(mock_bind_manager.consumer_bind_manager.return_value.bind.return_value, result)

        #Make sure we didn't process the agent
        self.assertFalse(mock_bind_manager.consumer_agent_manager.called)

    @patch('pulp.server.tasks.consumer.managers')
    def test_bind_with_agent_notification(self, mock_bind_manager):
        binding_config = {'binding': 'foo'}
        agent_options = {'bar': 'baz'}
        mock_bind_manager.consumer_agent_manager.return_value.bind.return_value = 'foo-id'
        result = consumer.bind('foo_consumer_id', 'foo_repo_id', 'foo_distributor_id',
                               True, binding_config, agent_options)
        mock_bind_manager.consumer_agent_manager.return_value.bind.assert_called_once_with(
            'foo_consumer_id', 'foo_repo_id', 'foo_distributor_id', agent_options
        )

        self.assertTrue(isinstance(result, TaskResult))
        self.assertEquals(result.return_value,
                          mock_bind_manager.consumer_bind_manager.return_value.bind.return_value)
        self.assertEquals(result.spawned_tasks, ['foo-id'])


class TestUnbind(unittest.TestCase):

    @patch('pulp.server.tasks.consumer.managers')
    def test_unbind_no_agent_notification(self, mock_bind_manager):
        binding_config = {'notify_agent': False}
        agent_options = {'bar': 'baz'}
        mock_bind_manager.consumer_bind_manager.return_value.get_bind.return_value = binding_config
        result = consumer.unbind('foo_consumer_id', 'foo_repo_id', 'foo_distributor_id',
                                 agent_options)

        mock_bind_manager.consumer_bind_manager.return_value.delete.assert_called_once_with(
            'foo_consumer_id', 'foo_repo_id', 'foo_distributor_id', True)

        self.assertEquals(None, result)

        #Make sure we didn't process the agent
        self.assertFalse(mock_bind_manager.consumer_agent_manager.called)

    @patch('pulp.server.tasks.consumer.managers')
    def test_unbind_with_agent_notification(self, mock_bind_manager):
        binding_config = {'notify_agent': True}
        agent_options = {'bar': 'baz'}
        mock_bind_manager.consumer_bind_manager.return_value.get_bind.return_value = binding_config
        mock_bind_manager.consumer_agent_manager.return_value.unbind.return_value = 'foo-id'
        result = consumer.unbind('foo_consumer_id', 'foo_repo_id', 'foo_distributor_id',
                                 agent_options)
        mock_bind_manager.consumer_agent_manager.return_value.unbind.assert_called_once_with(
            'foo_consumer_id', 'foo_repo_id', 'foo_distributor_id', agent_options)
        self.assertTrue(isinstance(result, TaskResult))
        self.assertEquals(result.spawned_tasks, ['foo-id'])


class TestForceUnbind(unittest.TestCase):
    @patch('pulp.server.tasks.consumer.managers')
    def test_unbind_no_agent_notification(self, mock_bind_manager):
        binding_config = {'notify_agent': False}
        agent_options = {'bar': 'baz'}
        mock_bind_manager.consumer_bind_manager.return_value.get_bind.return_value = binding_config
        result = consumer.force_unbind('foo_consumer_id', 'foo_repo_id', 'foo_distributor_id',
                                       agent_options)

        mock_bind_manager.consumer_bind_manager.return_value.delete.assert_called_once_with(
            'foo_consumer_id', 'foo_repo_id', 'foo_distributor_id', True)

        self.assertEquals(None, result)

        #Make sure we didn't process the agent
        self.assertFalse(mock_bind_manager.consumer_agent_manager.called)

    @patch('pulp.server.tasks.consumer.managers')
    def test_unbind_with_agent_notification(self, mock_bind_manager):
        binding_config = {'notify_agent': True}
        agent_options = {'bar': 'baz'}
        mock_bind_manager.consumer_bind_manager.return_value.get_bind.return_value = binding_config
        mock_bind_manager.consumer_agent_manager.return_value.unbind.return_value = 'foo-id'
        result = consumer.force_unbind('foo_consumer_id', 'foo_repo_id', 'foo_distributor_id',
                                       agent_options)
        mock_bind_manager.consumer_agent_manager.return_value.unbind.assert_called_once_with(
            'foo_consumer_id', 'foo_repo_id', 'foo_distributor_id', agent_options)
        self.assertTrue(isinstance(result, TaskResult))
        self.assertEquals(result.spawned_tasks, ['foo-id'])
