include ../resources/lm/Manifest.py

blank_xml="""<udm.DeploymentPackage version="ClaimsBPM_Baseline" application="BPM">
  <orchestrator />
  <deployables />
  <applicationDependencies />
</udm.DeploymentPackage>"""
existing_xml="""<udm.DeploymentPackage version="ClaimsBPM_Baseline" application="BPM">
  <orchestrator />
  <deployables>
    <lmwas.ApplicationBindingSpec name="POSTDEPLOY_RecoveriesMediationModule">
      <tags />
      <bindings>
        <lmwas.ActivationSpecMaxConcurrencySpec name="POSTDEPLOY_RecoveriesMediationModule/setActivationSpecMaxConcurrency">
          <activationSpecName>RecoveriesMediationModule</activationSpecName>
          <maxConcurrency>1</maxConcurrency>
        </lmwas.ActivationSpecMaxConcurrencySpec>
      </bindings>
    </lmwas.ApplicationBindingSpec>
  </deployables>
  <applicationDependencies />
</udm.DeploymentPackage>"""

deployable_xml="""<list> <lmwas.ApplicationBindingSpec name="POSTDEPLOY_RecoveriesMediationModule">
      <tags />
      <bindings>
        <lmwas.ActivationSpecMaxConcurrencySpec name="POSTDEPLOY_RecoveriesMediationModule/setActivationSpecMaxConcurrency">
          <activationSpecName>RecoveriesMediationModule</activationSpecName>
          <maxConcurrency>1</maxConcurrency>
        </lmwas.ActivationSpecMaxConcurrencySpec>
      </bindings>
    </lmwas.ApplicationBindingSpec>
    <was.J2CConnectionFactorySpec name="J2CFF_CSW_JDBC_ORCL_CF">
      <tags>
        <value>BPMallNodes</value>
      </tags>
      <provider>IBM WebSphere Adapter for JDBC</provider>
      <jndiName>jdbc/CSW_JDBC_ORCL_CF</jndiName>
      <customProperties>
        <entry key="adapterID">ResourceAdapter</entry>
        <entry key="logFileSize">0</entry>
        <entry key="connectionRetryInterval">60000</entry>
        <entry key="Password">{{cswJdbcCfPassword}}</entry>
        <entry key="connectionRetryLimit">0</entry>
        <entry key="errorOnEmptyResultset">true</entry>
        <entry key="XADataSourceJNDIName">jdbc/Claims</entry>
        <entry key="hideConfidentialTrace">false</entry>
        <entry key="DatabaseVendor">DB2</entry>
        <entry key="logNumberOfFiles">1</entry>
        <entry key="connectionType">XADataSourceJNDI</entry>
        <entry key="AutoCommit">false</entry>
      </customProperties>
    </was.J2CConnectionFactorySpec>
    """

single_deployable="""<lmwas.ModulePropertySpec name="POSTDEPLOY_ESubroHubMediationModule/ModuleProprty_ProcessCorrectDemandTransformedXMLTrace.">
          <moduleName>ESubroHubMediationModule</moduleName>
          <propertyName>[ESubroHubMediationModule.ESubroHubMediationModule]ProcessCorrectDemandTransformedXMLTrace.enabled</propertyName>
          <propertyValue>false</propertyValue>
        </lmwas.ModulePropertySpec>
      </bindings>
    </lmwas.ApplicationBindingSpec>"""



#