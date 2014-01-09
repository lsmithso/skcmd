(require 'dbus)

(defvar skcmd-sname "uk.co.opennet.skypecmd_service")
(defvar skcmd-iname "uk.co.opennet.skypecmd_interface")
(defvar skcmd-path "/SkypeObject")



(defun skcmd-status-handler(caller_id status)
  (when myes-announce
    (dtk-tone 1200 200 t) 
    (dtk-tone 1900 200 t)
    (message "Skype : %s %s" caller_id status)))

(defun skcmd-register-signal()
  (dbus-register-signal
   :session skcmd-sname skcmd-path skcmd-iname
   "signal_call_status" 'skcmd-status-handler ))

(skcmd-register-signal)

(defun skcmd-call(method &rest args)
  (apply 'dbus-call-method
	 :session ; use the session (not system) bus
	 skcmd-sname
	 skcmd-path
	 skcmd-iname
	 method args))

(defun skcall ()
  (interactive)
  (let* (
	 (b
	  (if (region-active-p)
	      (buffer-substring (region-beginning) (region-end))
""))
	 (target (read-from-minibuffer "Skype call to: " b))
	 (target (replace-regexp-in-string  "[ \t]" "" target))
	 (clean-number (replace-regexp-in-string "^0" "+44" target)))
    (message "skype call to: %s" clean-number)
    (skcmd-call "call" clean-number)))




(defun skend ()
  (interactive)
(skcmd-call "hangup"))

(defun skanswer ()
(interactive)
(skcmd-call "answer"))

(defun sktone ()
(interactive)
(skcmd-call "tone" (read-from-minibuffer "Tone: ")))



(provide 'skcmd)

(message "skcmd loaded")



