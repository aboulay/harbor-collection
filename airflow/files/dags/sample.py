from airflow import DAG
from datetime import datetime, timedelta
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.contrib.kubernetes.volume import Volume
from airflow.contrib.kubernetes.volume_mount import VolumeMount
from airflow.operators.dummy_operator import DummyOperator


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.utcnow(),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'kubernetes_sample',
    default_args=default_args,
    schedule_interval=timedelta(minutes=10)
)


start = DummyOperator(task_id='run_this_first', dag=dag)

k8s = KubernetesPodOperator(
    namespace='default',
    image="aquasec/kube-bench:latest",
    cmds=["kube-bench", "--json", "--logtostderr"],
    labels={"app": "kube-bench"},
    name="kube-bench",
    task_id="kube-bench",
    volumes=[
        Volume(name="var-lib-etcd", configs={'hostPath': {"path": "/var/lib/etcd"}}),
        Volume(name="var-lib-kubelet", configs={'hostPath': {"path": "/var/lib/kubelet"}}),
        Volume(name="etc-systemd", configs={'hostPath': {"path": "/etc/systemd"}}),
        Volume(name="etc-kubernetes", configs={'hostPath': {"path": "/etc/kubernetes"}}),
        Volume(name="usr-bin", configs={'hostPath': {"path": "/usr/bin"}}),
    ],
    volumes_mounts=[
        VolumeMount('var-lib-etcd', mount_path='/var/lib/etcd', sub_path="", read_only=True),
        VolumeMount('var-lib-kubelet', mount_path='/var/lib/kubelet', sub_path="", read_only=True),
        VolumeMount('etc-systemd', mount_path='/etc/systemd', sub_path="", read_only=True),
        VolumeMount('etc-kubernetes', mount_path='/etc/kubernetes', sub_path="", read_only=True),
        VolumeMount('usr-bin', mount_path='/usr/bin', sub_path="", read_only=True),
    ],
    get_logs=True,
    dag=dag
)

k8s.set_upstream(start)