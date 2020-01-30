# {{job_name}}

{% if job_success %}
_Job succeeded!_
{% else %}
**Job failed!**
{% endif %}

[Link to job page]({[job_link]})

---

{% if additional_info %}
**Additional job information:**

{% if no_output %}
- No output was generated! This could be due to test participants crashing or failing to start, please check the log files for more information.
{% endif %}

{% if message %}
- {{message}}
{% endif %}

{% endif %}
