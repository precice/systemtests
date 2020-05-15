# {{job_name}}

Job type: {{ type }}


{% if job_success %}
**Job succeeded!**
{% else %}
**Job failed!**
{% endif %}

{% if is_pr %}
This build was triggered by a pull request from `{{pr_branch}}` → `{{branch}}`.
{% else %}
This build was triggered by a push to `{{branch}}`.
{% endif %}


[Link to job page]({[job_link]})


This job folder contains
- A `Logs` directory containing log files from TravisCI and the participant containers
{% if output_enabled %}
- An `Output` directory containing result files generated during the running of the test
{% endif %}

---

{% if additional_info %}
**Additional job information:**

{% if output_enabled %}
- Output was enabled for this job.
{% if not output_missing %}
	- Result files have been stored in the `Output` folder.
{% else %}
	- **No result files were generated!** This could be due to test participants crashing or failing to start, please check the logs (in the `Logs` directory or on TravisCI) for more information.
{% endif %}
- Output was not enabled for this run, no result files were stored. _If you wish to enable output, execute the `push.py` script with the added argument `-o`_
{% endif %}

{% if logs_missing %}
- No logs from were generated! Check the TravisCI job page noted above to see what went wrong.
{% endif %}


{% if message %}
- {{message}}
{% endif %}

{% endif %}
