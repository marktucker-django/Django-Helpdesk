"""                                     .. 
                                 .,::;::::::
                           ..,::::::::,,,,:::      Jutda Helpdesk - A Django
                      .,,::::::,,,,,,,,,,,,,::     powered ticket tracker for
                  .,::::::,,,,,,,,,,,,,,,,,,:;r.        small enterprise
                .::::,,,,,,,,,,,,,,,,,,,,,,:;;rr.
              .:::,,,,,,,,,,,,,,,,,,,,,,,:;;;;;rr      (c) Copyright 2008
            .:::,,,,,,,,,,,,,,,,,,,,,,,:;;;:::;;rr
          .:::,,,,,,,,,,,,,,,,,,,,.  ,;;;::::::;;rr           Jutda
        .:::,,,,,,,,,,,,,,,,,,.    .:;;:::::::::;;rr
      .:::,,,,,,,,,,,,,,,.       .;r;::::::::::::;r;   All Rights Reserved
    .:::,,,,,,,,,,,,,,,        .;r;;:::::::::::;;:.
  .:::,,,,,,,,,,,,,,,.       .;r;;::::::::::::;:.
 .;:,,,,,,,,,,,,,,,       .,;rr;::::::::::::;:.   This software is released 
.,:,,,,,,,,,,,,,.    .,:;rrr;;::::::::::::;;.  under a limited-use license that
  :,,,,,,,,,,,,,..:;rrrrr;;;::::::::::::;;.  allows you to freely download this
   :,,,,,,,:::;;;rr;;;;;;:::::::::::::;;,  software from it's manufacturer and
    ::::;;;;;;;;;;;:::::::::::::::::;;,  use it yourself, however you may not
    .r;;;;:::::::::::::::::::::::;;;,  distribute it. For further details, see
     .r;::::::::::::::::::::;;;;;:,  the enclosed LICENSE file.
      .;;::::::::::::::;;;;;:,.
       .;;:::::::;;;;;;:,.  Please direct people who wish to download this
        .r;;;;;;;;:,.  software themselves to www.jutda.com.au.
          ,,,..

$Id$

"""
from datetime import datetime, timedelta, date
from django.db.models import Q
from helpdesk.models import EscalationExclusion, Queue
import sys, getopt

day_names = {
    'monday': 0,
    'tuesday': 1,
    'wednesday': 2,
    'thursday': 3,
    'friday': 4,
    'saturday': 5,
    'sunday': 6,
}

def create_exclusions(days, occurrences, verbose, queues):
    days = days.split(',')
    for day in days:
        day_name = day
        day = day_names[day]
        workdate = date.today()
        i = 0
        while i < occurrences:
            if day == workdate.weekday():
                if EscalationExclusion.objects.filter(date=workdate).count() == 0:
                    esc = EscalationExclusion(name='Auto Exclusion for %s' % day_name, date=workdate)
                    esc.save()
                
                    if verbose:
                        print "Created exclusion for %s %s" % (day_name, workdate)
                
                    for q in queues:
                        esc.queues.add(q)
                        if verbose:
                            print "  - for queue %s" % q

                i += 1
            workdate += timedelta(days=1)


def usage():
    print "Options:"
    print " --days, -d: Days of week (monday, tuesday, etc)"
    print " --occurrences, -o: Occurrences: How many weeks ahead to exclude this day"
    print " --queues, -q: Queues to include (default: all). Use queue slugs"
    print " --verbose, -v: Display a list of dates excluded"

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'd:o:q:v', ['days=', 'occurrences=', 'verbose', 'queues='])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    
    days = None
    occurrences = None
    verbose = False
    queue_slugs = None
    queues = []

    for o, a in opts:
        if o in ('-v', '--verbose'):
            verbose = True
        if o in ('-d', '--days'):
            days = a
        if o in ('-q', '--queues'):
            queue_slugs = a
        if o in ('-o', '--occurrences'):
            occurrences = int(a)

    if not occurrences: occurrences = 1
    if not (days and occurrences):
        usage()
        sys.exit(2)
    
    if queue_slugs is not None:
        queue_set = queue_slugs.split(',')
        for queue in queue_set:
            try:
                q = Queue.objects.get(slug__exact=queue)
            except:
                print "Queue %s does not exist." % queue
                sys.exit(2)
            queues.append(q)

    create_exclusions(days=days, occurrences=occurrences, verbose=verbose, queues=queues)
