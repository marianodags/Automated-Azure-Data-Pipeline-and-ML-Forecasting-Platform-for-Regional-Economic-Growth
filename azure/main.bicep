// Azure Infrastructure as Code (Bicep) Template
// Deploys Azure SQL Database, Azure Blob Storage, Azure Functions, and Azure Data Factory
targetScope = 'resourceGroup'

param location string = resourceGroup().location
param environmentName string = 'prod'
param sqlAdminLogin string = 'sqladmin'
@secure()
param sqlAdminPassword string

var prefix = 'econintel-${environmentName}'

// 1. Storage Account (Azure Blob Storage for Data Lake)
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: replace('${prefix}store', '-', '')
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
  }
}

resource blobContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  name: '${storageAccount.name}/default/rawdata'
}

// 2. Azure SQL Database Server & Database
resource sqlServer 'Microsoft.Sql/servers@2022-05-01-preview' = {
  name: '${prefix}-sqlserver'
  location: location
  properties: {
    administratorLogin: sqlAdminLogin
    administratorLoginPassword: sqlAdminPassword
  }
}

resource sqlDB 'Microsoft.Sql/servers/databases@2022-05-01-preview' = {
  parent: sqlServer
  name: 'regional_economy_db'
  location: location
  sku: {
    name: 'Basic'
    tier: 'Basic'
  }
}

// Firewall rule to allow Azure Services
resource sqlFirewall 'Microsoft.Sql/servers/firewallRules@2022-05-01-preview' = {
  parent: sqlServer
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// 3. Azure Data Factory
resource dataFactory 'Microsoft.DataFactory/factories@2018-06-01' = {
  name: '${prefix}-adf'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
}

// 4. Azure Function App (Automation Trigger)
resource appServicePlan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: '${prefix}-asp'
  location: location
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
  }
}

resource functionApp 'Microsoft.Web/sites@2022-09-01' = {
  name: '${prefix}-func'
  location: location
  kind: 'functionapp'
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      appSettings: [
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
      ]
    }
  }
}

output sqlServerFQDN string = sqlServer.properties.fullyQualifiedDomainName
output storageAccountName string = storageAccount.name
output dataFactoryName string = dataFactory.name
output functionAppName string = functionApp.name
