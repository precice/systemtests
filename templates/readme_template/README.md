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

{% if output_missing %}
- No output was generated! This could be due to test participants crashing or failing to start, please check the log files for more information.
{% endif %}

{% if logs_missing %}
- No logs from were generated! Check the TravisCI job page noted above to see what went wrong.
{% endif %}


{% if message %}
- {{message}}
{% endif %}

{% endif %}
