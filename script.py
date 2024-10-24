import json
import subprocess
import time

REPO = "https://github.com/acoronadoc/python-deployment-script-sample.git"
BRANCH = "master"
CHECK_INTERVAL = 5

def exec( cmd, cwd=".", returnjson=False ):
  out = subprocess.run( cmd, capture_output=True, text=True, encoding="utf8", cwd=cwd )

  if ( out.returncode != 0 ):
    print( "", flush=True )
    print( "ERROR EXECUTING TASK: %s " % out.args, flush=True)
    print( "STDOUT: %s " % out.stdout, flush=True )
    print( "STDERR: %s " % out.stderr, flush=True )
    print( "", flush=True )

    return None

  if ( returnjson ):
    return json.loads( out.stdout )

  return out

def process_pipeline():
    r = exec( [ "rm", "-R", "-f", "dir1" ] )

    r = exec( [ "git", "clone", REPO, "dir1" ] )

    r = exec( [ "kubectl", "apply", "-f", "kubernetes/sampleapp.yaml" ] )

    r = exec( [ "kubectl", "cp", "script.py", "nginx-statefulset-0:/usr/share/nginx/html" ] )

    r = exec( [ "/bin/bash", "-c" ,"kubectl exec -it pod/nginx-statefulset-0 -- /bin/sh -c 'date > /usr/share/nginx/html/index.html'" ] )
    r = exec( [ "/bin/bash", "-c" ,"kubectl exec -it pod/nginx-statefulset-0 -- /bin/sh -c 'echo '' >> /usr/share/nginx/html/index.html'" ] )
    r = exec( [ "/bin/bash", "-c" ,"kubectl exec -it pod/nginx-statefulset-0 -- /bin/sh -c 'echo '' >> /usr/share/nginx/html/index.html'" ] )
    r = exec( [ "/bin/bash", "-c" ,"kubectl exec -it pod/nginx-statefulset-0 -- /bin/sh -c 'cat /usr/share/nginx/html/script.py >> /usr/share/nginx/html/index.html'" ] )
    
last_commit = ""

while True: 
    r = exec( [ "git", "ls-remote", "--heads", REPO ] )
    #print( r )

    commits = r.stdout.splitlines()
    commits = filter( lambda x: x.endswith( "refs/heads/" + BRANCH ), commits )
    commits = list( map( lambda x: x.split( "\t" ), commits ) )

    if last_commit != "" and last_commit != commits[0][0]:
       print( "Processint new commit: %s" % commits[0][0] )

       last_commit = commits[0][0]

       process_pipeline()
    else:
       print( "No new commit found: %s" % last_commit )


    time.sleep( CHECK_INTERVAL )

