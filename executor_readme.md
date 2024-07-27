# Generate .exe file

1. Install pyinstaller (if not installed)
   * pip install pyinstaller
2. Navigate to the automation project
3. Open command prompt (Path should be pointing to automation project)
4. Run script (executor_script) in terminal/cmd
   * Wait till executor_script run is successfully completed
5. You can get app.exe file at /dist path


# Run executor file
1. Open command prompt
2. Change directory to the path where app.exe is located
3. In command prompt, directly run app.exe
   * Once the service is successfully running
   * You can access swagger at mentioned url
   * Example: http://127.0.0.1:2024/docs

# Access Automation Service
1. Click on Authorize at top right corner
2. Provide Access Token
    * Note: You can get Access Token from respective FTDM Application
      * Login
      * Go to Setting (Top right corner)
      * Go to Master Configuration
      * Go to Access Tokens
      * If token already exists, copy the token and pass to Automation Service -> Authorize field
      * If not create a new token and pass the same to Automation Service -> Authorize
3. You can see two fields at Automate Logbook Services
   * Encrypt Payload
     * Check in your corresponding FTDM application for any of the APIs if payload are being passed in JWT encrypted format
     * If encrypted, selected Encrypt Payload as True else False
   * File
     * Select the Logbook Template configured
4. Finally Execute the Service