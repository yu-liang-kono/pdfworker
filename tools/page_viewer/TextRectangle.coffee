Rectangle = (x, y, w, h, args) ->

	@x = x
	@y = y
	@w = w
	@h = h
	@args = args

Rectangle.prototype =

	constructor: Rectangle

	clone: () -> new Rectangle(@x, @y, @w, @h, @args)

	area: () -> @w * @h

	vertices: () ->

		[[@x, @y], [@x + @w, @y], [@x + @w, @y + @h], [@x, @y + @h]]

	distance: (other) ->

		if @intersect(other) then return 0

		minDist = Infinity
		vertices = other.vertices()

		for v1, i in @vertices()
			for v2, j in vertices
				dx = v1[0] - v2[0]
				dy = v1[1] - v2[1]
				d = dx * dx + dy * dy
				minDist = d if d < minDist

		minDist

	union: (other) ->

		minX = Math.min(@x, other.x)
		minY = Math.min(@y, other.y)
		maxX = Math.max(@x + @w, other.x + other.w)
		maxY = Math.max(@y + @h, other.y + other.h)

		new Rectangle(minX, minY, maxX - minX, maxY - minY)

	intersect: (other) ->

		lineIntersect = (line1, line2) ->

			left = line1
			right = line2
			if right[0] < left[0]
				[left, right] = [right, left]

			if not (left[0] <= right[0] < left[1])
				return null

			if right[1] >= left[1]
				return [right[0], left[1]]

			right

		intersectX = lineIntersect([@x, @x + @w], [other.x, other.x + other.w])
		if not intersectX
			return null

		intersectY = lineIntersect([@y, @y + @h], [other.y, other.y + other.h])
		if not intersectY
			return null

		new Rectangle(intersectX[0], intersectY[0],
					  intersectX[1] - intersectX[0],
					  intersectY[1] - intersectY[0])


RectangleGroup = () ->

	@elements = _.filter arguments, (arg) -> arg instanceof Rectangle
	@minBoundingRectangle = null

	if @elements.length is 0
		return
	else
		@minBoundingRectangle = @elements[0]
		for r, i in @elements
			if i > 0 then @minBoundingRectangle = @minBoundingRectangle.union(@elements[i])

	return

RectangleGroup.prototype =

	constructor: RectangleGroup

	distance: (other) ->

		@minBoundingRectangle.distance(other.minBoundingRectangle)

	union: (other) ->

		ret = new RectangleGroup()
		ret.elements = (r.clone() for r in @elements)
		ret.minBoundingRectangle = @minBoundingRectangle.clone()

		for r in other.elements
			ret.elements.push(r)
			ret.minBoundingRectangle = ret.minBoundingRectangle.union(r)

		ret

window.Rectangle = Rectangle
window.RectangleGroup = RectangleGroup