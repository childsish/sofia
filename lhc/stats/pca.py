def pca(X):
    """ rows are dimensions (positions), cols are observations (genotypes) """
    # Calculate the PCA
    U, S, V = linalg.svd(snps)
    X = dot(snps, V.T)
    return V.T, S, X

def nipals(X, npc=3, e=1e-8, maxiter=100):
    """ This method should work on very large matrices.
     rows are dimensions, cols are observations """
    # Run NIPAL
    res = empty((X.shape[0], npc))
    for i in xrange(npc):
        u = X[:,0]
        for j in xrange(maxiter):
            v = dot(X.T, u) / dot(u.T, u)
            v /= linalg.norm(v)
            u_old = u
            u = dot(X, v) / dot(v.T, v)
            d = linalg.norm(u_old - u)
            if d < e:
                break
        res[:,i] = dot(X, v) # Get only the projected data (not normalised to v * v.T)
        for j in xrange(X.shape[0]):
            for k in xrange(X.shape[1]):
                X[j, k] -= u[j] * v[k]
    return res
