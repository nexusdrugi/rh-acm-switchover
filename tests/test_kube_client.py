"""Unit tests for lib/kube_client.py."""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

from kubernetes.client.rest import ApiException

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.kube_client import KubeClient


class TestKubeClient(unittest.TestCase):
    """Test cases for KubeClient class."""

    def setUp(self) -> None:
        self.config_patcher = patch('lib.kube_client.config.load_kube_config')
        self.mock_load_config = self.config_patcher.start()

        self.custom_api_patcher = patch('lib.kube_client.client.CustomObjectsApi')
        self.mock_custom_cls = self.custom_api_patcher.start()
        self.mock_custom_api = self.mock_custom_cls.return_value

        self.core_api_patcher = patch('lib.kube_client.client.CoreV1Api')
        self.mock_core_cls = self.core_api_patcher.start()
        self.mock_core_api = self.mock_core_cls.return_value

        self.apps_api_patcher = patch('lib.kube_client.client.AppsV1Api')
        self.mock_apps_cls = self.apps_api_patcher.start()
        self.mock_apps_api = self.mock_apps_cls.return_value

        self.client = KubeClient(context="test-context", dry_run=False)
        self.dry_run_client = KubeClient(context="test-context", dry_run=True)

    def tearDown(self) -> None:
        for patcher in (
            self.apps_api_patcher,
            self.core_api_patcher,
            self.custom_api_patcher,
            self.config_patcher,
        ):
            patcher.stop()

    def test_get_custom_resource(self):
        self.mock_custom_api.get_namespaced_custom_object.return_value = {
            "metadata": {"name": "test"}
        }

        result = self.client.get_custom_resource(
            "operator.open-cluster-management.io",
            "v1",
            "multiclusterhubs",
            "test-hub",
            namespace="test-ns",
        )

        self.assertIsNotNone(result)
        self.mock_custom_api.get_namespaced_custom_object.assert_called_once_with(
            group="operator.open-cluster-management.io",
            version="v1",
            namespace="test-ns",
            plural="multiclusterhubs",
            name="test-hub",
        )

    def test_get_custom_resource_not_found(self):
        self.mock_custom_api.get_namespaced_custom_object.side_effect = ApiException(status=404)

        result = self.client.get_custom_resource(
            "operator.open-cluster-management.io",
            "v1",
            "multiclusterhubs",
            "test-hub",
            namespace="test-ns",
        )

        self.assertIsNone(result)

    def test_list_custom_resources(self):
        self.mock_custom_api.list_namespaced_custom_object.return_value = {
            "items": [
                {"metadata": {"name": "cluster1"}},
                {"metadata": {"name": "cluster2"}},
            ]
        }

        result = self.client.list_custom_resources(
            "cluster.open-cluster-management.io",
            "v1",
            "managedclusters",
            namespace="test-ns",
        )

        self.assertEqual(len(result), 2)
        self.mock_custom_api.list_namespaced_custom_object.assert_called_once()

    def test_patch_custom_resource_dry_run(self):
        result = self.dry_run_client.patch_custom_resource(
            "cluster.open-cluster-management.io",
            "v1",
            "managedclusters",
            name="test-cluster",
            patch={"spec": {"paused": True}},
            namespace="test-ns",
        )

        self.assertEqual(result, {})
        self.mock_custom_api.patch_namespaced_custom_object.assert_not_called()

    def test_patch_custom_resource_normal(self):
        self.mock_custom_api.patch_namespaced_custom_object.return_value = {"result": True}

        result = self.client.patch_custom_resource(
            "cluster.open-cluster-management.io",
            "v1",
            "managedclusters",
            name="test-cluster",
            patch={"spec": {"paused": True}},
            namespace="test-ns",
        )

        self.assertTrue(result)
        self.mock_custom_api.patch_namespaced_custom_object.assert_called_once()

    def test_create_custom_resource_dry_run(self):
        resource_body = {
            "apiVersion": "cluster.open-cluster-management.io/v1beta1",
            "kind": "Restore",
            "metadata": {"name": "test-restore"},
        }

        result = self.dry_run_client.create_custom_resource(
            "cluster.open-cluster-management.io",
            "v1beta1",
            "restores",
            body=resource_body,
            namespace="test-ns",
        )

        self.assertEqual(result, resource_body)
        self.mock_custom_api.create_namespaced_custom_object.assert_not_called()

    def test_delete_custom_resource_dry_run(self):
        result = self.dry_run_client.delete_custom_resource(
            "cluster.open-cluster-management.io",
            "v1",
            "managedclusters",
            name="test-cluster",
            namespace="test-ns",
        )

        self.assertTrue(result)
        self.mock_custom_api.delete_namespaced_custom_object.assert_not_called()

    def test_scale_deployment_dry_run(self):
        result = self.dry_run_client.scale_deployment(
            namespace="test-ns",
            name="test-deploy",
            replicas=3,
        )

        self.assertEqual(result, {})
        self.mock_apps_api.patch_namespaced_deployment_scale.assert_not_called()

    def test_scale_deployment_normal(self):
        response = MagicMock()
        response.to_dict.return_value = {"status": "scaled"}
        self.mock_apps_api.patch_namespaced_deployment_scale.return_value = response

        result = self.client.scale_deployment(
            namespace="test-ns",
            name="test-deploy",
            replicas=3,
        )

        self.assertEqual(result, {"status": "scaled"})
        self.mock_apps_api.patch_namespaced_deployment_scale.assert_called_once()

    def test_scale_statefulset(self):
        response = MagicMock()
        response.to_dict.return_value = {"status": "scaled"}
        self.mock_apps_api.patch_namespaced_stateful_set_scale.return_value = response

        result = self.client.scale_statefulset(
            namespace="test-ns",
            name="test-sts",
            replicas=0,
        )

        self.assertEqual(result, {"status": "scaled"})
        self.mock_apps_api.patch_namespaced_stateful_set_scale.assert_called_once()

    def test_namespace_exists(self):
        self.mock_core_api.read_namespace.return_value = MagicMock()

        result = self.client.namespace_exists("test-ns")

        self.assertTrue(result)
        self.mock_core_api.read_namespace.assert_called_once_with("test-ns")

    def test_namespace_not_exists(self):
        self.mock_core_api.read_namespace.side_effect = ApiException(status=404)

        result = self.client.namespace_exists("test-ns")

        self.assertFalse(result)

    def test_get_pods(self):
        pod1 = MagicMock()
        pod1.to_dict.return_value = {"metadata": {"name": "pod1"}}
        pod2 = MagicMock()
        pod2.to_dict.return_value = {"metadata": {"name": "pod2"}}
        self.mock_core_api.list_namespaced_pod.return_value.items = [pod1, pod2]

        result = self.client.get_pods("test-ns", label_selector="app=test")

        self.assertEqual(len(result), 2)
        self.mock_core_api.list_namespaced_pod.assert_called_once_with(
            namespace="test-ns",
            label_selector="app=test",
        )

    @patch('lib.kube_client.time.sleep')
    def test_wait_for_pods_ready(self, mock_sleep):
        pod_not_ready = MagicMock()
        pod_not_ready.to_dict.return_value = {
            "metadata": {"name": "pod1"},
            "status": {"conditions": [{"type": "Ready", "status": "False"}]},
        }
        pod_ready = MagicMock()
        pod_ready.to_dict.return_value = {
            "metadata": {"name": "pod1"},
            "status": {"conditions": [{"type": "Ready", "status": "True"}]},
        }

        self.mock_core_api.list_namespaced_pod.side_effect = [
            MagicMock(items=[pod_not_ready]),
            MagicMock(items=[pod_ready]),
        ]

        result = self.client.wait_for_pods_ready("test-ns", "app=test", timeout=10)

        self.assertTrue(result)
        self.assertGreaterEqual(self.mock_core_api.list_namespaced_pod.call_count, 2)

    def test_rollout_restart_deployment_dry_run(self):
        result = self.dry_run_client.rollout_restart_deployment(
            namespace="test-ns",
            name="test-deploy",
        )

        self.assertEqual(result, {})
        self.mock_apps_api.patch_namespaced_deployment.assert_not_called()

    def test_rollout_restart_deployment_normal(self):
        response = MagicMock()
        response.to_dict.return_value = {"status": "restarted"}
        self.mock_apps_api.patch_namespaced_deployment.return_value = response

        result = self.client.rollout_restart_deployment(
            namespace="test-ns",
            name="test-deploy",
        )

        self.assertEqual(result, {"status": "restarted"})
        self.mock_apps_api.patch_namespaced_deployment.assert_called_once()


class TestKubeClientInitialization(unittest.TestCase):
    """Test cases for KubeClient initialization."""

    @patch('lib.kube_client.config.load_kube_config')
    def test_init_with_context(self, mock_load_config):
        KubeClient(context="test-context")
        mock_load_config.assert_called_once_with(context="test-context")

    @patch('lib.kube_client.config.load_kube_config')
    def test_init_without_context(self, mock_load_config):
        KubeClient()
        mock_load_config.assert_called_once_with(context=None)

    @patch('lib.kube_client.config.load_kube_config')
    def test_init_dry_run_flag(self, mock_load_config):
        client_normal = KubeClient(dry_run=False)
        client_dry = KubeClient(dry_run=True)

        self.assertFalse(client_normal.dry_run)
        self.assertTrue(client_dry.dry_run)


if __name__ == '__main__':
    unittest.main()
