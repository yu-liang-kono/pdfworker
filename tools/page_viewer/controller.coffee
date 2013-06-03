PageController = ($scope) ->

	$scope.pageData = null
	$scope.numCluster = 1
	$scope.cluster = []

	$scope.readFile = () ->

		file = document.getElementById('file-input').files[0]
		reader = new FileReader()

		reader.readAsText(file)
		reader.onloadend = () ->

			$scope.$apply () ->

				$scope.pageData = JSON.parse(reader.result)
				$scope.cluster = []
				$scope.numCluster = 1
				for data in $scope.pageData.data
					$scope.cluster.push(0)
					data.c = 0

				_.defer () ->
					$text = $('.text')
					$text.each () ->
						$this = $(@)
						w = $this.outerWidth()
						h = $this.outerHeight()
						defaultWidth = parseFloat($this.attr('data-width'))
						defaultHeight = parseFloat($this.attr('data-height'))
						$this.css('-webkit-transform', "scale(#{defaultWidth / w}, #{defaultHeight / h})")

	$scope.getClusterColor = (cluster) ->

		return "hsla(0, 0, 0, 0)" if $scope.numCluster is 1

		"hsla(#{Math.round(360 / $scope.numCluster * cluster)}, 50%, 50%, 0.5)"

	initKmeans = () ->

		clusterCenters = []

		shuffled = _.shuffle(_.range($scope.pageData.data.length))

		_($scope.numCluster).times (i) ->
			data = $scope.pageData.data[shuffled[i]]
			$scope.cluster[shuffled[i]] = i
			clusterCenters.push [data.x + data.w / 2, data.y + data.h / 2]

		clusterCenters

	$scope.kmeans = () ->

		numData = $scope.pageData.data.length
		numChangeCluster = $scope.numCluster

		# randomly pick up centroid
		clusterCenters = initKmeans()

		# main loop
		while numChangeCluster > 0
			numChangeCluster = 0

			# assign phase
			for data, i in $scope.pageData.data
				minDist = Infinity
				nearestCenter = -1

				_($scope.numCluster).times (j) ->
					center = clusterCenters[j]
					d = (data.x - center[0]) * (data.x - center[0]) + (data.y - center[1]) * (data.y - center[1])
					if d < minDist
						minDist = d
						nearestCenter = j

				if nearestCenter isnt $scope.cluster[i]
					$scope.cluster[i] = nearestCenter
					numChangeCluster++

			# minimize phase
			_($scope.numCluster).times (j) ->
				myCluster = []
				sumX = 0
				sumY = 0
				numDataInCluster = 0

				for c, i in $scope.cluster
					if c is j
						sumX += $scope.pageData.data[i].x + $scope.pageData.data[i].w / 2
						sumY += $scope.pageData.data[i].y + $scope.pageData.data[i].h / 2
						numDataInCluster++

				clusterCenters[j] = [sumX / numDataInCluster, sumY / numDataInCluster]

		_.each($scope.cluster, (c, i) -> $scope.pageData.data[i].c = c)
		return

	$scope.numHierarchyCluster = 1
	$scope.hierarchyCluster = () ->

		rectangleGroupIndices = []
		allRectangleGroups = {}

		# initialize
		for data, i in $scope.pageData.data
			$scope.cluster.push(i)
			data.c = i

			rect = new Rectangle(data.x, data.y, data.w, data.h)
			rectGrp = new RectangleGroup(rect)

			rectID = _.uniqueId()
			allRectangleGroups[rectID] = rectGrp
			rectangleGroupIndices.push(rectID)

		while _.keys(allRectangleGroups).length > $scope.numHierarchyCluster
			# compute rectangle distance between each rectangle
			idGrpPairs = _.pairs allRectangleGroups

			minDist = Infinity
			closestPairs = null
			for idGrpPair1, i in idGrpPairs
				for idGrpPair2, j in idGrpPairs
					if i >= j then continue

					d = idGrpPair1[1].distance(idGrpPair2[1])
					if d < minDist
						minDist = d
						closestPairs = [idGrpPair1[0], idGrpPair2[0]]

			mergerID = closestPairs[0]
			merger = allRectangleGroups[mergerID]
			mergeeID = closestPairs[1]
			mergee = allRectangleGroups[mergeeID]

			# merge the closest rectangle pair
			for rgi, k in rectangleGroupIndices
				if rgi is mergeeID
					rectangleGroupIndices[k] = mergerID

			allRectangleGroups[mergerID] = merger.union(mergee)
			delete allRectangleGroups[mergeeID]

		clusterIndex = 0
		for rectID, rect of allRectangleGroups
			for rgi, i in rectangleGroupIndices
				if rgi is rectID then $scope.pageData.data[i].c = clusterIndex

			clusterIndex += 1

		$scope.numCluster = $scope.numHierarchyCluster

		return

	return

window.PageController = PageController