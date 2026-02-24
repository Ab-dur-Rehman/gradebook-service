# gradebook-service

The department's gradebook. Records students, assessments and marks; reports percentages.

```bash
python3 gradebook.py          # http://localhost:8000
```

```bash
curl -X POST localhost:8000/students     -d '{"id":"S1","name":"Ayesha"}'
curl -X POST localhost:8000/assessments  -d '{"id":"A1","title":"Quiz 1","weight":"10","total":"20"}'
curl -X POST localhost:8000/marks        -d '{"student":"S1","assessment":"A1","score":"15"}'
curl localhost:8000/students/S1
curl localhost:8000/report
```

It works. That is the only claim made for it.
