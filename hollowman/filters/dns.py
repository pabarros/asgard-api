#encoding: utf-8

import json

class DNSRequestFilter(object):

  def run(self, request):
    if request.is_json and request.data:
      body = request.get_json()
      if self.is_single_app(body):
          body = self.patch_app_dns_parameters(body)
      if self.is_multi_app(body):
          for app in body:
              self.patch_app_dns_parameters(app)
      if self.is_group(body):
          self.patch_apps_from_group(body)
      request.data = json.dumps(body)
    return request

  def is_single_app(self, data):
     has_groups = 'groups' in data
     has_apps = 'apps' in data
     is_dict = isinstance(data, dict)
     return is_dict and not has_groups and not has_apps

  def is_multi_app(self, data):
     is_list = isinstance(data, list)
     return is_list and not self.is_single_app(data)

  def is_docker_app(self, data):
      has_container = 'container' in data
      has_docker = has_container and ('docker' in data['container'])
      return has_docker

  def is_group(self, data):
     has_groups = 'groups' in data
     has_apps = 'apps' in data
     return has_groups or has_apps

  def get_apps_from_group(self, group):
      if 'apps' in group:
          return group['apps']
      return []

  def patch_app_dns_parameters(self, data):
      if self.is_docker_app(data):
          data['container']['docker']['parameters'] = [
            {
                "key": "dns",
                "value": "172.17.0.1"
            }        
          ]
      return data

  def patch_apps_from_group(self, group):
      for app in self.get_apps_from_group(group):
          self.patch_app_dns_parameters(app)
      if 'groups' in group:
          for subgroup in group['groups']:
              self.patch_apps_from_group(subgroup)
