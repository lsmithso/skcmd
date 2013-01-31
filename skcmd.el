(require 'dbus)

(defvar skcmd-sname "uk.co.opennet.skypecmd_service")
(defvar skcmd-iname "uk.co.opennet.skypecmd_interface")
(defvar skcmd-path "/SkypeObject")


(setq skcmd-announce-enabled t)

(defun skcmd-status-handler(caller_id status)
  (when skcmd-announce-enabled
    (dtk-tone 1200 200 t) 
    (dtk-tone 1900 200 t)
    (message "Skype : %s %s" caller_id status)))

(defun skcmd-register-signal()
  (dbus-register-signal
   :session skcmd-sname skcmd-path skcmd-iname
   "signal_call_status" 'skcmd-status-handler ))

(skcmd-register-signal)
(message "skcmd registered")
(provide 'skcmd)


