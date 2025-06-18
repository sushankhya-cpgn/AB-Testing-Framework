from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index
from scipy.stats import norm, ttest_ind, chi2_contingency
from numpy import format_float_scientific
from collections import defaultdict
import random
import enum
from datetime import datetime
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:rootpass@localhost/ab_testing_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ExperimentStatus(enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"

class MetricType(enum.Enum):
    BINARY = "binary"
    CONTINUOUS = "continuous"
    CATEGORICAL = "categorical"

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    assignments = db.relationship("Assignment", backref="user", cascade="all, delete-orphan")
    sample_size_assignments = db.relationship("SampleSizeUser", backref="user", cascade="all, delete-orphan")

class Experiment(db.Model):
    __tablename__ = 'experiment'
    experiment_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.Enum(ExperimentStatus), nullable=False)
    metric_type = db.Column(db.Enum(MetricType), nullable=False, default=MetricType.BINARY)
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
    metric_type = db.Column(db.Enum(MetricType), nullable=False, default=MetricType.BINARY)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    metric_results = db.relationship("MetricResult", backref="metric", cascade="all, delete-orphan")

class MetricResult(db.Model):
    __tablename__ = 'metric_result'
    result_id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.assignment_id'), nullable=False, index=True)
    metric_id = db.Column(db.Integer, db.ForeignKey('metric.metric_id'), nullable=False, index=True)
    value = db.Column(db.Float, nullable=False)  # Float to support continuous values
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = (
        db.UniqueConstraint('assignment_id', 'metric_id', name='unique_assignment_metric'),
        Index('idx_assignment_metric', 'assignment_id', 'metric_id')
    )

class SampleSizeUser(db.Model):
    __tablename__ = 'sample_size_user'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False, index=True)
    experiment_id = db.Column(db.Integer, db.ForeignKey('experiment.experiment_id'), nullable=False, index=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.assignment_id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = (
        db.UniqueConstraint('user_id', 'experiment_id', name='unique_sample_user_experiment'),
        Index('idx_sample_user_experiment', 'user_id', 'experiment_id'),
    )


@app.route('/create_experiment', methods=['POST'])
def create_experiment():
    data = request.json
    logger.debug(f"Creating experiment: {data}")
    try:
        exp = Experiment(
            name=data['name'],
            start_date=datetime.strptime(data['start_date'], "%Y-%m-%d"),
            end_date=datetime.strptime(data['end_date'], "%Y-%m-%d"),
            status=ExperimentStatus.ACTIVE,
            metric_type=MetricType[data['metric_type'].upper()]
        )
        db.session.add(exp)
        db.session.commit()
        for variant_name in data['variants']:
            db.session.add(Variant(name=variant_name, experiment_id=exp.experiment_id))
        db.session.commit()
        return jsonify({"message": "Experiment created", "experiment_id": exp.experiment_id})
    except Exception as e:
        logger.error(f"Error creating experiment: {e}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/assign_user', methods=['POST'])
def assign_user():
    data = request.json
    logger.debug(f"Assigning user: {data}")
    email = data['email']
    experiment_id = data['experiment_id']
    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email)
            db.session.add(user)
            db.session.commit()
        variants = Variant.query.filter_by(experiment_id=experiment_id).all()
        if not variants:
            return jsonify({"error": "No variants found for this experiment"}), 404
        chosen_variant = random.choice(variants)
        existing_assignment = Assignment.query.join(Variant).filter(
            Assignment.user_id == user.user_id,
            Variant.experiment_id == experiment_id
        ).first()
        if existing_assignment:
            return jsonify({
                "message": "User already assigned",
                "variant": existing_assignment.variant.name,
                "assignment_id": existing_assignment.assignment_id,
                "user_id": existing_assignment.user_id
            })
        assignment = Assignment(user_id=user.user_id, variant_id=chosen_variant.variant_id)
        db.session.add(assignment)
        db.session.commit()
        return jsonify({
            "message": "User assigned",
            "variant": chosen_variant.name,
            "assignment_id": assignment.assignment_id,
            "user_id": user.user_id
        })
    except Exception as e:
        logger.error(f"Error assigning user: {e}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/record_metric', methods=['POST'])
def record_metric():
    data = request.json
    logger.debug(f"Recording metric: {data}")
    try:
        metric = Metric.query.filter_by(name=data['metric']).first()
        if not metric:
            metric = Metric(
                name=data['metric'],
                description="Auto-created",
                metric_type=MetricType[data['metric_type'].upper()] if 'metric_type' in data else MetricType.BINARY
            )
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
    except Exception as e:
        logger.error(f"Error recording metric: {e}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

   
@app.route('/add_sample_size_user', methods=['POST'])
def add_sample_size_user():
    data = request.json
    logger.debug(f"Adding sample size user: {data}")
    try:
        user_id = data['user_id']
        experiment_id = data['experiment_id']
        assignment_id = data['assignment_id']
        existing = SampleSizeUser.query.filter_by(user_id=user_id, experiment_id=experiment_id).first()
        if existing:
            return jsonify({"message": "User already in sample size for this experiment"}), 400
        sample_user = SampleSizeUser(
            user_id=user_id,
            experiment_id=experiment_id,
            assignment_id=assignment_id
        )
        db.session.add(sample_user)
        db.session.commit()
        return jsonify({"message": "Sample size user added"})
    except Exception as e:
        logger.error(f"Error adding sample size user: {e}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/experiments', methods=['GET'])
def list_experiments():
    try:
        experiments = Experiment.query.filter_by(status=ExperimentStatus.ACTIVE).all()
        return jsonify([
            {
                "experiment_id": exp.experiment_id,
                "name": exp.name,
                "start_date": exp.start_date.strftime("%Y-%m-%d"),
                "end_date": exp.end_date.strftime("%Y-%m-%d") if exp.end_date else None,
                "variants": [v.name for v in exp.variants],
                "metric_type": exp.metric_type.value
            }
            for exp in experiments
        ])
    except Exception as e:
        logger.error(f"Error listing experiments: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/analyze/<int:experiment_id>')
def analyze_experiment(experiment_id):
    logger.debug(f"Analyzing experiment ID: {experiment_id}")
    try:
        experiment = Experiment.query.get(experiment_id)
        if not experiment:
            return jsonify({"error": "Experiment not found"}), 404
        variants = Variant.query.filter_by(experiment_id=experiment_id).all()
        if len(variants) < 2:
            return jsonify({"error": "At least two variants are required for analysis"}), 400

        # Collect data from SampleSizeUser
        data = {}
        for variant in variants:
            sample_assignments = SampleSizeUser.query.join(Assignment).filter(
                SampleSizeUser.experiment_id == experiment_id,
                Assignment.variant_id == variant.variant_id
            ).all()
            assignment_ids = [sa.assignment_id for sa in sample_assignments]
            if not assignment_ids:
                continue
            results = MetricResult.query.filter(
                MetricResult.assignment_id.in_(assignment_ids),
                MetricResult.metric.has(name=experiment.name.lower().replace(" ", "_"))
            ).all()
            if not results:
                continue
            data[variant.name] = [r.value for r in results]

        if len(data) < 2:
            return jsonify({"error": "Not enough data for analysis"}), 400

        analysis_results = []
        metric_type = experiment.metric_type

        if metric_type == MetricType.BINARY:
            # Z-test for binary metrics
            variant_names = list(data.keys())
            num_comparisons = len(variant_names) * (len(variant_names) - 1) // 2
         
            if len(variant_names) == 2:
                    v1, v2 = variant_names[0], variant_names[1]
                    x1, n1 = sum(data[v1]), len(data[v1])
                    x2, n2 = sum(data[v2]), len(data[v2])
                    p_pool = (x1 + x2) / (n1 + n2)
                    se = (p_pool * (1 - p_pool) * (1/n1 + 1/n2)) ** 0.5
                    z = (x1/n1 - x2/n2) / se
                    p_value = 2 * (1 - norm.cdf(abs(z)))
                    alpha = 0.05
                    analysis_results.append({
                        "variant_1": v1,
                        "variant_2": v2,
                        "conversion_rate_1": round(x1/n1, 4),
                        "conversion_rate_2": round(x2/n2, 4),
                        "z_statistic": round(z, 4),
                        "p_value": format_float_scientific(p_value, precision=2),
                        "significant": "Yes" if p_value < alpha else "No"
                    })

        elif metric_type == MetricType.CONTINUOUS:
            # T-test for continuous metrics
            variant_names = list(data.keys())
            num_comparisons = len(variant_names) * (len(variant_names) - 1) // 2
            alpha_corrected = 0.05 / num_comparisons
            for i in range(len(variant_names)):
                for j in range(i + 1, len(variant_names)):
                    v1, v2 = variant_names[i], variant_names[j]
                    values1, values2 = data[v1], data[v2]
                    t_stat, p_value = ttest_ind(values1, values2, equal_var=False)  # Welch's t-test
                    analysis_results.append({
                        "variant_1": v1,
                        "variant_2": v2,
                        "mean_1": round(sum(values1)/len(values1), 4),
                        "mean_2": round(sum(values2)/len(values2), 4),
                        "t_statistic": round(t_stat, 4),
                        "p_value": float(f"{p_value:.2e}"),
                        "significant": "Yes" if p_value < alpha_corrected else "No"
                    })

        elif metric_type == MetricType.CATEGORICAL:
            # Chi-square test for categorical metrics
            variant_names = list(data.keys())
            categories = sorted(set(val for vals in data.values() for val in vals))
            contingency_table = [[sum(1 for v in data[vn] if v == cat) for cat in categories] for vn in variant_names]
            chi2_stat, p_value, _, _ = chi2_contingency(contingency_table)
            analysis_results.append({
                "variants": variant_names,
                "chi2_statistic": round(chi2_stat, 4),
                "p_value": float(f"{p_value:.2e}"),
                "significant": "Yes" if p_value < 0.05 else "No"
            })

        return jsonify({
            "experiment": {
                "experiment_id": experiment.experiment_id,
                "name": experiment.name,
                "status": experiment.status.value,
                "metric_type": metric_type.value
            },
            "analysis": analysis_results
        })
    except Exception as e:
        logger.error(f"Error analyzing experiment: {e}")
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)

