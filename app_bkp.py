from flask import Flask, request,render_template, session, redirect, url_for, Response, stream_with_context
# from src.logger import logging
# from src.pipeline.event_pipeline import eventPipeline
import logging 
# import concurrent.futures # new
# import uuid # new
import json 
import threading 
import queue
import os 

app = Flask(__name__)
app.secret_key = "qsko12uh49"

app.config['SESSION_PERMANENT'] = False

# background executor and in-memory job store
# executor = concurrent.futures.ThreadPoolExecutor(max_workers=2) # new
# jobs = {} # new


@app.route('/new_session')
def new_session():
    session.clear()
    return redirect(url_for('index'))

@app.route('/', methods=['GET', 'POST'])
def index():
    session.permanent = False 
    session.setdefault('event_urls', [])

    # status/result placeholders
    # success = None # new
    # total = None # new
    # job_status = None # new

    if request.method == 'POST':
        action = request.form.get('action', 'add')

        if action == 'add':
            url = request.form.get('URL', '').strip()
            if url:
                urls = session['event_urls']
                urls.append(url)
                session['event_urls'] = urls

        elif action == 'clear':
            urls = session.get('event_urls', [])
            session.pop('event_urls', None)

            try:
                from src.pipeline.event_pipeline import eventPipeline
            except Exception:
                logging.exception("Failed to import eventPipeline")
                return redirect(url_for('index'))
            
 
            
            import threading 
            def run_pipeline(u):
                try:
                    eventPipeline(u)

                except Exception:
                    logging.exception("eventPipeline failed")
            threading.Thread(target=run_pipeline, args=(urls,), daemon=True).start()
            # success = True 
            # total = len(urls)

        # Redirect to GET to show updated list and avoid form resubmission
        return redirect(url_for('index'))

    return render_template('index.html', event_urls=session.get('event_urls', []))
                        #    , s = success, t = total)








# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8000)