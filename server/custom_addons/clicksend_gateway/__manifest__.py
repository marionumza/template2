# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Clicksend SMS Gateway",
  "summary"              :  "Flectra Clicksend SMS Gateway module allows Flectra admin to send SMS using ClickSend SMS. The user can send easy text message to clients.",
  "category"             :  "Marketing",
  "version"              :  "1.0.1",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-ClickSend-SMS-Gateway.html",
  "description"          :  """ClickSend communication
Flectra ClickSend SMS Gateway
Click Send SMS Gateway
ClickSend SMS alert
Use ClickSend in Flectra
Integrate SMS Gateways with Flectra
Bulk SMS send
Send Bulk SMS
ClickSend communication
ClickSend Flectra
Click Send
Flectra SMS Notification
Send Text Messages to mobile
Integrate SMS Gateways with Flectra
SMS Gateway
SMS Notification
Notify with Flectra SMS 
Mobile message send
Send Mobile messages
Mobile notifications to customers
Mobile Notifications to Users
How to get SMS notification in Flectra
module to get SMS notification in Flectra
SMS Notification app in Flectra
Notify SMS in Flectra
Add SMS notification feature to your Flectra
Mobile SMS feature
How Flectra can help to get SMS notification,
Flectra SMS OTP Authentication,
Marketplace SMS
Plivo SMS Gateway
Skebby SMS Gateway
Mobily SMS Gateway
MSG91 SMS Gateway
Netelip SMS Gateway
Twilio SMS Gateway
""",
  "live_test_url"        :  "https://webkul.com/blog/odoo-clicksend-sms-gateway/",
  "depends"              :  ['sms_notification'],
  "data"                 :  [
                             'views/clicksend_config_view.xml',
                             'views/sms_report.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  50,
  "currency"             :  "EUR",
  "external_dependencies":  {'python': ['urllib3']},
}