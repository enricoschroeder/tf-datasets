# coding=utf-8
# Copyright 2024 The TensorFlow Datasets Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for file_utils."""

import os
import time
from unittest import mock

from absl.testing import flagsaver
from etils import epath
import pytest
from tensorflow_datasets import testing
from tensorflow_datasets.core import naming
from tensorflow_datasets.core.utils import file_utils
from tensorflow_datasets.core.utils import read_config


def test_default_data_dir():
  data_dir = file_utils.get_default_data_dir(given_data_dir=None)
  assert data_dir
  assert isinstance(data_dir, str)


def test_list_dataset_variants_with_configs(mock_fs: testing.MockFs):
  data_dir = epath.Path('/a')
  dataset_dir = data_dir / 'my_ds'
  configs_and_versions = {
      'x': ['1.0.0', '1.0.1'],
      'y': ['2.0.0'],
  }
  for config, versions in configs_and_versions.items():
    for version in versions:
      mock_fs.add_file(dataset_dir / config / version / 'dataset_info.json')
      mock_fs.add_file(dataset_dir / config / version / 'features.json')

  references = sorted(file_utils.list_dataset_variants(dataset_dir=dataset_dir))
  assert references == [
      naming.DatasetReference(
          dataset_name='my_ds', config='x', version='1.0.0', data_dir=data_dir
      ),
      naming.DatasetReference(
          dataset_name='my_ds', config='x', version='1.0.1', data_dir=data_dir
      ),
      naming.DatasetReference(
          dataset_name='my_ds', config='y', version='2.0.0', data_dir=data_dir
      ),
  ]


def test_list_dataset_variants_with_configs_no_versions(
    mock_fs: testing.MockFs,
):
  data_dir = epath.Path('/a')
  dataset_dir = data_dir / 'my_ds'
  configs_and_versions = {
      'x': ['1.0.0', '1.0.1'],
      'y': ['2.0.0'],
  }
  for config, versions in configs_and_versions.items():
    for version in versions:
      mock_fs.add_file(dataset_dir / config / version / 'dataset_info.json')
      mock_fs.add_file(dataset_dir / config / version / 'features.json')

  references = sorted(
      file_utils.list_dataset_variants(
          dataset_dir=dataset_dir, include_versions=False
      )
  )
  assert references == [
      naming.DatasetReference(
          dataset_name='my_ds', config='x', data_dir=data_dir
      ),
      naming.DatasetReference(
          dataset_name='my_ds', config='y', data_dir=data_dir
      ),
  ]


def test_list_dataset_variants_without_configs(mock_fs: testing.MockFs):
  data_dir = epath.Path('/a')
  dataset_dir = data_dir / 'my_ds'
  # Version 1.0.0 doesn't have features.json, because it was generated with an
  # old version of TFDS.
  mock_fs.add_file(dataset_dir / '1.0.0' / 'dataset_info.json')
  mock_fs.add_file(dataset_dir / '1.0.1' / 'dataset_info.json')
  mock_fs.add_file(dataset_dir / '1.0.1' / 'features.json')

  # List dirs including datasets generated by old TFDS versions.
  references = sorted(
      file_utils.list_dataset_variants(
          dataset_dir=dataset_dir,
          include_versions=True,
          include_old_tfds_version=True,
      )
  )
  assert references == [
      naming.DatasetReference(
          dataset_name='my_ds', version='1.0.0', data_dir=data_dir
      ),
      naming.DatasetReference(
          dataset_name='my_ds', version='1.0.1', data_dir=data_dir
      ),
  ]

  # List dirs excluding datasets generated by old TFDS versions.
  references = sorted(
      file_utils.list_dataset_variants(
          dataset_dir=dataset_dir,
          include_versions=True,
          include_old_tfds_version=False,
      )
  )
  assert references == [
      naming.DatasetReference(
          dataset_name='my_ds', version='1.0.1', data_dir=data_dir
      )
  ]


if __name__ == '__main__':
  testing.test_main()
