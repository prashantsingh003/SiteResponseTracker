|**S. No.**|**API Route**|**Function Name**|**Methods Allowed**|**Authentication**|**Form Fields Required**|
| - | - | - | - | - | - |
|1|home|home||FALSE||
|2|sign-up|sign\_up|GET,POST|FALSE|email, password, username|
|3|log-in|log\_in|GET,POST|FALSE|email, password|
|4|deactivate-account|deactivate\_account|DELETE|TRUE||
|5|website/add|add\_website|GET,POST|TRUE|url|
|6|website/remove/ <int:website\_id>|remove\_website|DELETE|TRUE||
|7|website/update/<website\_id>|update\_website|GET,PUT, POST|TRUE||
|8|website/<website\_id>|get\_site\_report|GET|TRUE||
|9|website/all|fetch\_websites|GET|TRUE||
|10|website/notification/<int:website\_id>|change\_notification|GET,POST|TRUE||
|11|forgot\_password|forgot\_password|GET,POST|FALSE|email|
|12|reset\_password/<encoded\_email>/<forgot\_password\_hash>|generate\_email\_forget\_password|GET|FALSE||
|13|reset\_password/<encoded\_email>|reset\_password|GET,POST|FALSE|Password|
|14|pay/<price\_id>|on\_create\_session|POST|TRUE||
|15|article-details|article\_details|GET|FALSE||
|16|policy|policy|GET|FALSE||
|17|terms-and-conditions|terms\_conditions|GET|FALSE||
|18|pricing|pricing|GET,POST|FALSE||


|**Output**|**Required Parameters**|**Error Response**|**Comments**||||
| - | - | - | - | - | - | :- |
|Homepage|None||The home template used index.html as parent html file||||
|Signup page|None||Doesn’t allow duplicate emails||||
|Login page|None||Generates and sends a JWT token back||||
||None||Sets account to inactive||||
|Add website page|None||||||
|Removes the website from tracking|None||||||
|Updates the website|None||||||
||None||Current site’s performance||||
|Fetches all the websites that are registered under the current user|None||Returns all the website linked to current user||||
|Changes the notification status in the database,And returns the current status|None||||||
||None||Sends a link reset link to users email||||
||None||Is the format of link sent||||
||None||Requires a new password to set||||
|Redirects to stripe payment gateway|None||Redirects user to stripe’s checkout page||||
|Article detail page|None||||||
||None||||||
||None||||||
|Pricing page|None||||||


||
| - |
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

