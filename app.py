from flask import Flask, request,render_template, session, redirect, url_for, Response, stream_with_context
# from src.logger import logging
# from src.pipeline.event_pipeline import eventPipeline
from src.logger import logging 
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

# Global progress store
'''
progress code blocks are new editions
http://127.0.0.1:8000
'''
progress_queues = {}

@app.route('/progress/<session_id>')
def progress(session_id):
    def event_stream():
        q = progress_queues.get(session_id)
        if not q:
            return 
        while True:
            message = q.get()
            yield f"data: {json.dumps(message)}\n\n"
            if message.get("done"):
                break 
    return Response(stream_with_context(event_stream()), mimetype="text/event-stream")

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

        elif action == 'clear_list':
        # Just clears the URL list and resets session, no pipeline
            session.pop('event_urls', None)
            session.pop('session_id', None)

        elif action == 'clear':
            urls = session.get('event_urls', [])
            session.pop('event_urls', None)

        

            session_id = session.get('session_id', os.urandom(8).hex()) # new code block
            session['session_id'] = session_id # new code block

            q = queue.Queue() # new code block
            progress_queues[session_id] = q # new code block

            try:
                from src.pipeline.event_pipeline import eventPipeline
            except Exception:
                logging.exception("Failed to import eventPipeline")
                return redirect(url_for('index'))
            
 
            def run_pipeline(u, q, total):
                try:
                    for index, url in enumerate(u, 1):
                        q.put({
                            "index": index,
                            "total": total,
                            "url": url,
                            "status": "processing"

                        })
                        eventPipeline([url])
                        q.put({
                            "index": index,
                            "total": total,
                            "url": url,
                            "status": "done"
                        })
                except Exception:
                    logging.exception("eventPipeline failed")
                    q.put({"error": True, "done": True})
                finally:
                    q.put({"done":True})

            threading.Thread(
                target=run_pipeline,
                args=(urls, q, len(urls)),
                daemon=True
            ).start()
        
            
        return redirect(url_for('index'))
        
    return render_template('index.html',
                            event_urls=session.get('event_urls',[]),
                            session_id=session.get('session_id')
                            )




if __name__ == "__main__":
    app.run()
    # app.run(host="0.0.0.0", port=8000)