# KEDA-RabbitMQ-K8s

## Deploy RabbitMQ

```
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install rabbitmq bitnami/rabbitmq --set auth.username=guest --set auth.password=guestpassword -n test
```

## Install KEDA

```
helm repo add kedacore https://kedacore.github.io/charts
helm install keda kedacore/keda --namespace keda --create-namespace
```

## Verifications

```
sambit@Sambit:~$ kubectl get all -n test
NAME             READY   STATUS    RESTARTS   AGE
pod/rabbitmq-0   1/1     Running   0          140m

NAME                        TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)                                 AGE
service/rabbitmq            ClusterIP   10.96.116.209   <none>        5672/TCP,4369/TCP,25672/TCP,15672/TCP   140m
service/rabbitmq-headless   ClusterIP   None            <none>        4369/TCP,5672/TCP,25672/TCP,15672/TCP   140m

NAME                        READY   AGE
statefulset.apps/rabbitmq   1/1     140m
sambit@Sambit:~$
```

```
sambit@Sambit:~$ kubectl get all -n keda
NAME                                                   READY   STATUS    RESTARTS       AGE
pod/keda-admission-webhooks-68bd947995-mgvng           1/1     Running   0              140m
pod/keda-operator-6fff99756c-8nm6p                     1/1     Running   1 (139m ago)   140m
pod/keda-operator-metrics-apiserver-6cfdff8b87-jc8ps   1/1     Running   0              140m

NAME                                      TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)            AGE
service/keda-admission-webhooks           ClusterIP   10.104.165.163   <none>        443/TCP            140m
service/keda-operator                     ClusterIP   10.108.178.143   <none>        9666/TCP           140m
service/keda-operator-metrics-apiserver   ClusterIP   10.100.138.75    <none>        443/TCP,8080/TCP   140m

NAME                                              READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/keda-admission-webhooks           1/1     1            1           140m
deployment.apps/keda-operator                     1/1     1            1           140m
deployment.apps/keda-operator-metrics-apiserver   1/1     1            1           140m

NAME                                                         DESIRED   CURRENT   READY   AGE
replicaset.apps/keda-admission-webhooks-68bd947995           1         1         1       140m
replicaset.apps/keda-operator-6fff99756c                     1         1         1       140m
replicaset.apps/keda-operator-metrics-apiserver-6cfdff8b87   1         1         1       140m
```

You can view RabbitMQ UI through 

```
kubectl port-forward svc/rabbitmq -n test 15672:15672
```

## Deployment RabbitMQ worker

```
kubectl apply -f rabbitMQ-worker.yaml -n test
```

## Deploy scaledobject

```
kubectl apply -f scaledObject.yaml -n test

sambit@Sambit:~$ kubectl get scaledobject -n test
NAME                    SCALETARGETKIND      SCALETARGETNAME   MIN   MAX   READY   ACTIVE   FALLBACK   PAUSED    TRIGGERS   AUTHENTICATIONS   AGE
rabbitmq-scaledobject   apps/v1.Deployment   rabbitmq-worker   0     5     True    True     False      Unknown   rabbitmq                     92s


Events:
  Type    Reason              Age   From           Message
  ----    ------              ----  ----           -------
  Normal  KEDAScalersStarted  9s    keda-operator  Scaler rabbitmq is built
  Normal  KEDAScalersStarted  9s    keda-operator  Started scalers watch
  Normal  ScaledObjectReady   9s    keda-operator  ScaledObject is ready for scaling
```

## Send messages

```
python producer.py
```

this will crete 500 messages

### Check scaling

```
sambit@Sambit:~$ kubectl get pods -n test
NAME                               READY   STATUS    RESTARTS   AGE
rabbitmq-0                         1/1     Running   0          151m
rabbitmq-worker-666bf6c967-hdkr6   1/1     Running   0          3s
sambit@Sambit:~$
```

kEDA events

```

Events:
  Type    Reason                      Age    From           Message
  ----    ------                      ----   ----           -------
  Normal  KEDAScalersStarted          3m34s  keda-operator  Scaler rabbitmq is built
  Normal  KEDAScalersStarted          3m34s  keda-operator  Started scalers watch
  Normal  ScaledObjectReady           3m34s  keda-operator  ScaledObject is ready for scaling
  Normal  KEDAScaleTargetActivated    50s    keda-operator  Scaled apps/v1.Deployment test/rabbitmq-worker from 0 to 1, triggered by rabbitMQScaler
  Normal  KEDAScaleTargetDeactivated  17s    keda-operator  Deactivated apps/v1.Deployment test/rabbitmq-worker from 1 to 0
```
