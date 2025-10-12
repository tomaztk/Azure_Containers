param location string = resourceGroup().location
param containerName string = 'hello-aci'
param dnsLabel string                         

@description('Container image to run')
param image string = 'mcr.microsoft.com/azuredocs/aci-helloworld:latest'

@minValue(0.25)
param cpu float = 1.0

@minValue(0.5)
param memory float = 1.5

resource cg 'Microsoft.ContainerInstance/containerGroups@2023-05-01' = {
  name: containerName
  location: location
  properties: {
    osType: 'Linux'
    restartPolicy: 'Always'
    containers: [
      {
        name: containerName
        properties: {
          image: image
          ports: [
            { port: 80 }
          ]
          resources: {
            requests: {
              cpu: cpu
              memoryInGB: memory
            }
          }
        }
      }
    ]
    ipAddress: {
      type: 'Public'
      ports: [
        { protocol: 'Tcp', port: 80 }
      ]
      dnsNameLabel: dnsLabel
    }
  }
}

output url string = 'http://${cg.properties.ipAddress.fqdn}'
