from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index,text
from scipy.stats import norm
# from statsmodels.stats.proportion import proportions_ztest


from collections import defaultdict
import random
import enum
from datetime import datetime

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ab_testing.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:rootpass@localhost/ab_testing_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



class ExperimentStatus(enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"

class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    assignments = db.relationship("Assignment", backref="user", cascade="all, delete-orphan")


class Experiment(db.Model):
    __tablename__ = 'experiment'

    experiment_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.Enum(ExperimentStatus), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    variants = db.relationship("Variant", backref="experiment", cascade="all, delete-orphan")


class Variant(db.Model):
    __tablename__ = 'variant'

    variant_id = db.Column(db.Integer, primary_key=True)
    experiment_id = db.Column(db.Integer, db.ForeignKey('experiment.experiment_id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    assignments = db.relationship("Assignment", backref="variant", cascade="all, delete-orphan")


class Assignment(db.Model):
    __tablename__ = 'assignment'

    assignment_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False, index=True)
    variant_id = db.Column(db.Integer, db.ForeignKey('variant.variant_id'), nullable=False, index=True)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    metric_results = db.relationship("MetricResult", backref="assignment", cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint('user_id', 'variant_id', name='unique_user_variant'),
        Index('idx_user_variant', 'user_id', 'variant_id'),
    )


class Metric(db.Model):
    __tablename__ = 'metric'

    metric_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    metric_results = db.relationship("MetricResult", backref="metric", cascade="all, delete-orphan")


class MetricResult(db.Model):
    __tablename__ = 'metric_result'

    result_id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.assignment_id'), nullable=False, index=True)
    metric_id = db.Column(db.Integer, db.ForeignKey('metric.metric_id'), nullable=False, index=True)
    value = db.Column(db.Float, nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('assignment_id', 'metric_id', name='unique_assignment_metric'),
        Index('idx_assignment_metric', 'assignment_id', 'metric_id')
    )

# Routes

@app.route('/create_experiment', methods=['POST'])
def create_experiment():
    data = request.json
    exp = Experiment(
    name=data['name'],
    start_date=datetime.strptime(data['start_date'], "%Y-%m-%d"),
    end_date=datetime.strptime(data['end_date'], "%Y-%m-%d"),
    status=ExperimentStatus.ACTIVE
)

    db.session.add(exp)
    db.session.commit()

    for variant_name in data['variants']:
        db.session.add(Variant(name=variant_name, experiment_id=exp.experiment_id))
    db.session.commit()
    return jsonify({"message": "Experiment created", "experiment_id": exp.experiment_id})

@app.route('/assign_user', methods=['POST'])
def assign_user():
    data = request.json
    email = data['email']
    experiment_id = data['experiment_id']

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email)
        db.session.add(user)
        db.session.commit()

    variants = Variant.query.filter_by(experiment_id=experiment_id).all()
    if not variants:
        return jsonify({"error": "No variants found for this experiment"}), 404

    chosen_variant = random.choice(variants)

    # Check if user already assigned to this experiment to avoid duplicate assignments
    existing_assignment = Assignment.query.join(Variant).filter(
        Assignment.user_id == user.user_id,
        Variant.experiment_id == experiment_id
    ).first()
    if existing_assignment:
        return jsonify({
            "message": "User already assigned",
            "variant": existing_assignment.variant.name,
            "assignment_id": existing_assignment.assignment_id
        })

    assignment = Assignment(user_id=user.user_id, variant_id=chosen_variant.variant_id)
    db.session.add(assignment)
    db.session.commit()

    return jsonify({
        "message": "User assigned",
        "variant": chosen_variant.name,
        "assignment_id": assignment.assignment_id
    })


@app.route('/record_metric', methods=['POST'])
def record_metric():
    data = request.json
    metric = Metric.query.filter_by(name=data['metric']).first()
    if not metric:
        metric = Metric(name=data['metric'], description="Auto-created")
        db.session.add(metric)
        db.session.commit()

    result = MetricResult(
        assignment_id=data['assignment_id'],
        metric_id=metric.metric_id,
        value=data['value']
    )
    db.session.add(result)
    db.session.commit()
    return jsonify({"message": "Metric recorded"})


@app.route('/results/<int:experiment_id>', methods=['GET'])
def results(experiment_id):
    variants = Variant.query.filter_by(experiment_id=experiment_id).all()
    response = {}

    for variant in variants:
        assignments = Assignment.query.filter_by(variant_id=variant.variant_id).all()
        assignment_ids = [a.assignment_id for a in assignments]

        results = MetricResult.query.filter(MetricResult.assignment_id.in_(assignment_ids)).all()
        if not results:
            avg_value = 0
        else:
            avg_value = sum(r.value for r in results) / len(results)

        response[variant.name] = {
            "assignments": len(assignments),
            "average_metric_value": avg_value
        }

    return jsonify(response)


@app.route('/analyze/<int:experiment_id>')
def analyze_experiment(experiment_id):
    experiment = Experiment.query.get(experiment_id)
    if not experiment:
        return jsonify({"error": "Experiment not found"}), 404

    variants = Variant.query.filter_by(experiment_id=experiment_id).all()
    if len(variants) < 2:
        return jsonify({"error": "At least two variants are required for analysis"}), 400

    # Collect data for each variant
    data = {}
    for variant in variants:
        assignments = Assignment.query.filter_by(variant_id=variant.variant_id).all()
        assignment_ids = [a.assignment_id for a in assignments]
        results_query = MetricResult.query.filter(
            MetricResult.assignment_id.in_(assignment_ids),
            MetricResult.metric.has(name='conversion')
        )
        results = results_query.all()

        conversions = sum(r.value for r in results)
        total = len(results)

        if total == 0:
            continue

        data[variant.name] = {
            "conversions": conversions,
            "total": total,
            "conversion_rate": conversions / total
        }

    if len(data) < 2:
        return jsonify({"error": "Not enough data for analysis"}), 400

    # Run Z-test for proportions between each pair of variants
    analysis_results = []
    variant_names = list(data.keys())
    for i in range(len(variant_names)):
        for j in range(i + 1, len(variant_names)):
            v1, v2 = variant_names[i], variant_names[j]
            x1, n1 = data[v1]['conversions'], data[v1]['total']
            x2, n2 = data[v2]['conversions'], data[v2]['total']

            # Pooled Proportion
            p_pool = (x1 + x2) / (n1 + n2)
            se = (p_pool * (1 - p_pool) * (1/n1 + 1/n2)) ** 0.5
            z = (x1/n1 - x2/n2) / se
            p_value = 2 * (1 - norm.cdf(abs(z)))  # Two-tailed test

            analysis_results.append({
                "variant_1": v1,
                "variant_2": v2,
                "conversion_rate_1": round(x1/n1, 4),
                "conversion_rate_2": round(x2/n2, 4),
                "z_statistic": round(z, 4),
                "p_value": float(f"{p_value:.12f}"),
                # "p_value": round(p_value, 4),
                "significant": "Yes" if p_value < 0.05 else "No"  # Convert boolean to string
            })

    return jsonify({
        "experiment": {
            "experiment_id": experiment.experiment_id,
            "name": experiment.name,
            "status": experiment.status.value  # Get the string value of the enum
        },
        "analysis": analysis_results
    })


from sqlalchemy import text  # Make sure this import exists

def setup_partitioned_table():
    try:
        # Step 1: Drop existing metric_result table if it exists
        db.session.execute(text("DROP TABLE IF EXISTS metric_result"))
        db.session.commit()

        # Step 2: Create partitioned metric_result table
        create_table_sql = """
        CREATE TABLE metric_result (
            result_id INT AUTO_INCREMENT,
            assignment_id INT NOT NULL,
            metric_id INT NOT NULL,
            value FLOAT NOT NULL,
            recorded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (result_id, assignment_id),
            UNIQUE KEY unique_assignment_metric (assignment_id, metric_id),
            KEY idx_assignment_metric (assignment_id, metric_id)
        )
        PARTITION BY RANGE (assignment_id) (
            PARTITION p0 VALUES LESS THAN (1000),
            PARTITION p1 VALUES LESS THAN (2000),
            PARTITION p2 VALUES LESS THAN (3000),
            PARTITION p3 VALUES LESS THAN MAXVALUE
        );
        """
        db.session.execute(text(create_table_sql))
        db.session.commit()
        print("✅ metric_result table created with partitioning.")
    except Exception as e:
        print("⚠️ Error creating partitioned table:", e)


if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()
    with app.app_context():
        setup_partitioned_table()
    app.run(debug=True, port=5001)
