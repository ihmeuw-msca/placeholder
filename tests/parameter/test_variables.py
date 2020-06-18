import numpy as np
import pandas as pd
import pytest

from anml.parameter.prior import GaussianPrior, Prior
from anml.parameter.variables import Variable, Intercept, VariableError

@pytest.fixture(scope='module')
def df():
    return pd.DataFrame({
        'cov1': np.arange(5),
        'cov2': np.random.randn(5) * 2, 
        'group': ['1', '2', '2', '1', '3'],
    })


@pytest.fixture(scope='module')
def variable():
    return Variable(
        covariate='cov1',
        var_link_fun=lambda x: x,
        fe_prior=GaussianPrior(lower_bound=[-2.0], upper_bound=[3.0]),
        add_re=True,
        col_group='group',
        re_var_prior=GaussianPrior(lower_bound=[-1.0], upper_bound=[1.0], mean=[1.0], std=[2.0]),
        re_prior=Prior(lower_bound=[-10.0], upper_bound=[15.0]),
    )


class TestBaseVariable:
    
    def test_variable(self, variable):
        assert isinstance(variable.fe_prior, Prior)
        assert variable.num_fe == 1
        assert variable.num_re_var == 1

    def test_encode_groups(self, df, variable):
        grp_assign_ord = variable.encode_groups(df)
        assert np.array_equal(grp_assign_ord, [0, 1, 1, 0, 2])
        assert variable.n_groups == 3

    def test_constraints(self, variable):
        variable.build_constraint_matrix()
        assert variable.constr_lb[0] == -2.0
        assert variable.constr_ub[0] == 3.0
        variable.build_constraint_matrix_re_var()
        assert variable.constr_lb_re_var[0] == -1.0
        assert variable.constr_ub_re_var[0] == 1.0
        variable.num_re = 3
        variable.build_constraint_matrix_re()
        np.testing.assert_allclose(variable.constr_matrix_re, np.identity(3))
        np.testing.assert_allclose(variable.constr_lb_re, -np.ones(3) * 10.0)
        np.testing.assert_allclose(variable.constr_ub_re, np.ones(3) * 15)

    def test_variable_design_matrices(self, df, variable):
        variable.build_design_matrix(df, build_re=True)
        np.testing.assert_allclose(
            variable.design_matrix,
            np.arange(5).reshape((-1, 1)),
        )
        assert variable.design_matrix_re.shape == (5, 3)

    def test_intercept(self, df):
        with pytest.raises(TypeError):
            i = Intercept(covariate='foo')
        i = Intercept()
        i.build_design_matrix(df)
        assert i.covariate == 'intercept'
        assert i.num_fe == 1
        np.testing.assert_allclose(
            i.design_matrix,
            np.ones((5, 1)),
        )
        i.build_constraint_matrix()
        assert i.constr_lb[0] == -np.inf
        assert i.constr_ub[0] == np.inf